import json
import random
import asyncio
from collections import namedtuple
from uuid import uuid4
import world
import base


class Game:
    ROOM_MODEL = namedtuple('Room', ['id', 'sockets', 'user_types'])
    USER_MODEL = namedtuple('User', ['room_id', 'type'])

    def __init__(self):
        self._waiting_rooms = dict()
        self._active_rooms = dict()
        self._socket_to_user = dict()

    async def update_world(self, websocket, message):
        try:
            user = self._socket_to_user[websocket]
        except KeyError:
            raise base.UserNotInRoom

        try:
            room = self._active_rooms[user.room_id]
        except KeyError:
            raise base.RoomInactive

        character = world.handle_input(user, message)

        if character:
            resp = dict(type='update',
                        character=character._asdict(),
                        user_type=user.type)

            await self.announce_to_room(room, resp)

    def create_user(self, websocket, room_id, user_type):
        user = self.USER_MODEL(room_id=room_id, type=user_type)
        self._socket_to_user[websocket] = user
        return user

    def create_room(self, sockets=None, user_types=None):
        return self.ROOM_MODEL(id=str(uuid4()),
                               sockets=sockets or set(),
                               user_types=user_types or set())

    async def add_to_room(self, room, websocket, user_type, announce=True):
        if websocket not in self._socket_to_user:
            self.create_user(websocket, room.id, user_type)

        room.sockets.add(websocket)
        room.user_types.add(user_type)

        if announce:
            await self.announce_join_room(room)

        return room.id

    async def fill_available_room(self, websocket, user_type):
        for key, room in self._waiting_rooms.items():
            if len(room.sockets) < 2 and user_type not in room.user_types:
                # once complete (i.e. has a Toro and a Torero),
                # the remove the room from the set of available rooms
                self._active_rooms[key] = self._waiting_rooms.pop(key)
                return await self.add_to_room(self._active_rooms[key],
                                              websocket, user_type)

    def announce_join_room(self, room):
        spectator_count = self.get_spectator_count(room)

        msg = dict(
                type='join', room_id=room.id,
                complete=base.PLAYABLE_USER_TYPES <= room.user_types,
                spectator_count=spectator_count)

        return self.announce_to_room(room, msg)

    def announce_leave_room(self, room, propagate=False):
        spectator_count = self.get_spectator_count(room)

        return self.announce_to_room(
            room, dict(type='leave', spectator_count=spectator_count,
                       propagate=propagate)
        )

    def get_spectator_count(self, room):
        return max(len(
            room.sockets
        ) - len(room.user_types - base.NONPLAYABLE_USER_TYPES), 0)

    async def announce_to_room(self, room, msg, exclude=None):
        serialized_msg = json.dumps(msg)

        await asyncio.gather(
            *[socket.send(serialized_msg)
              for socket in room.sockets
              if socket != exclude]
        )

        return msg

    async def create_room_and_user(self, websocket, user_type):
        room = self.create_room(sockets={websocket, },
                                user_types={user_type, })
        self.create_user(websocket, room.id, user_type)
        self._waiting_rooms[room.id] = room
        return room.id

    async def add_nonplayer_to_random_room(self, websocket, user_type):
        """
        if they are spectator send them
        to any room prioritizing active ones
        """
        rooms = self._active_rooms or self._waiting_rooms

        if rooms:
            room_id = random.choice(list(rooms.keys()))
            return await self.add_to_room(rooms[room_id], websocket, user_type)

    def attempt_to_join_room_and_create_user(self, websocket, user_type):
        # if a user wants to play, try to find a waiting room for them
        if user_type not in base.USER_TYPES:
            raise base.HandlerError(message='invalid user type')

        if user_type in base.PLAYABLE_USER_TYPES:
            return self.fill_available_room(websocket, user_type)

        return self.add_nonplayer_to_random_room(websocket, user_type)

    async def leave_room(self, websocket):
        try:
            user = self._socket_to_user.pop(websocket)
        except KeyError:
            raise base.UserNotInRoom

        # if the room is still waiting, just kill it
        room_is_waiting = user.room_id in self._waiting_rooms
        rooms = self._waiting_rooms if room_is_waiting else self._active_rooms
        room = rooms[user.room_id]
        room.sockets.remove(websocket)

        end_match = not room.sockets or user.type in base.PLAYABLE_USER_TYPES

        if end_match:
            for socket in room.sockets:
                del self._socket_to_user[socket]
            rooms.pop(room.id)

        await self.announce_leave_room(room, propagate=end_match)

    async def leave_room_if_connected(self, websocket):
        if websocket in self._socket_to_user:
            await self.leave_room(websocket)
