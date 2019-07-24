#!/usr/bin/env python

import random
import json
import asyncio
import websockets
import logging
import os
from collections import defaultdict, namedtuple
from uuid import uuid4

DEBUG = os.environ.get('DEBUG', True)

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT,
                    level=logging.DEBUG if DEBUG else logging.INFO)
MAIN_LOGGER = logging.getLogger('main')
PLAYABLE_USER_TYPES = {'TORO', 'TORERO'}
USER_TYPES = ('SPECTATOR', *PLAYABLE_USER_TYPES)

Room = namedtuple('Room', ['sockets', 'user_types'])
User = namedtuple('User', ['room_id', 'type'])


def defaultroom():
    return Room(sockets=set(), user_types=set())


def fill_available_room(websocket, user_type):
    for key, room in WAITING_ROOMS.items():
        if len(room.sockets) < 2 and user_type not in room.user_types:
            # once complete (i.e. has a Toro and a Torero),
            # the remove the room from the set of available rooms
            ACTIVE_ROOMS[key] = WAITING_ROOMS.pop(key)
            add_to_room(ACTIVE_ROOMS[key], websocket, user_type)
            return key


def format_error(msg):
    return json.dumps(dict(type='error', msg=msg))


def generate_room_id():
    return str(uuid4())


def create_room(websocket, user_type):
    room_id = generate_room_id()

    # since WAITING_ROOMS is a defaultdict,
    # accessing it at room_id, creates the underlying dict
    # (if not already there)
    add_to_room(WAITING_ROOMS[room_id], websocket, user_type)
    return json.dumps(dict(type='create', room_id=room_id))


def add_to_room(room, websocket, user_type):
    room.sockets.add(websocket)
    room.user_types.add(user_type)


async def announce_to_room(room, msg):
    await asyncio.gather(
        *[socket.send(msg) for socket in room.sockets])
    return msg


def announce_join_room(room, user):
    spectator_count = len(
        room.sockets
    ) - len(room.user_types - {'SPECTATOR', })

    return announce_to_room(
        room, json.dumps(dict(type='join', room_id=user.room_id,
                              complete=PLAYABLE_USER_TYPES <= room.user_types,
                              spectator_count=spectator_count))
    )


def announce_leave_room(room):
    return announce_to_room(
        room, json.dumps(dict(type='leave'))
    )


async def connect(websocket, message):
    user_type = message.get(
        'user_type',
        random.choice(list(PLAYABLE_USER_TYPES)))

    room_id = None

    # if the user already has a session, leave it
    if websocket in SOCKET_TO_USER:
        return leave_room(websocket)

    # if a user wants to play, try to find a waiting room for them
    if user_type in PLAYABLE_USER_TYPES:
        room_id = fill_available_room(websocket, user_type)

        if not room_id:
            return create_room(websocket, user_type)

    # if they are spectator send them to any room
    # prioritizing active ones
    rooms = ACTIVE_ROOMS or WAITING_ROOMS
    if not room_id and rooms:
        room_id = random.choice(list(rooms))
        add_to_room(rooms[room_id], websocket, user_type)

    user = User(room_id=room_id, type=user_type)
    SOCKET_TO_USER[websocket] = user

    await announce_join_room(rooms[room_id], user)


async def leave_room(websocket):
    try:
        room_id = SOCKET_TO_USER.pop(websocket)
    except KeyError:
        return format_error('socket not associated with a room')

    # if the room is still waiting, just kill it
    if room_id in WAITING_ROOMS:
        room = WAITING_ROOMS.pop(websocket)
    else:
        room = ACTIVE_ROOMS[room_id]
        room.sockets.remove(websocket)

        if not room.sockets:
            ACTIVE_ROOMS.pop(room_id)

    await announce_leave_room(room)


FRAME_TYPE_HANDLERS = {
    'connect': connect
}


WAITING_ROOMS = defaultdict(defaultroom)
ACTIVE_ROOMS = defaultdict(defaultroom)
SOCKET_TO_USER = dict()


async def main(websocket, path):
    try:
        async for frame in websocket:
            try:
                message = json.loads(frame)
            except TypeError as e:
                await websocket.send(format_error('frame not valid json'))

            try:
                resp = await FRAME_TYPE_HANDLERS[
                    message['type']](websocket, message)

                if resp:
                    await websocket.send(resp)
            except KeyError:
                await websocket.send(
                    format_error('frame malformed or type invalid'))
    finally:
        await leave_room(websocket)

start_server = websockets.serve(main, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
