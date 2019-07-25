import json
from base import HandlerError


class ToroWebSocketAPI:
    def __init__(self, game):
        self.game = game

    async def main(self, websocket, path):
        try:
            async for frame in websocket:
                try:
                    await self.handle_frame(websocket, frame)
                except HandlerError as e:
                    await self._send_to_socket(websocket, e.serialize())
                    raise e
        finally:
            await self.game.leave_room(websocket)

    async def handle_frame(self, websocket, frame):
        try:
            message = json.loads(frame)
        except TypeError as e:
            raise HandlerError('frame not valid json')

        try:
            await self.handle_message(websocket, message)
        except KeyError:
            raise HandlerError('frame malformed')

    def handle_message(self, websocket, message):
        message_type = message['type']

        if message_type == 'connect':
            return self.connect(websocket, message)
        elif message_type == 'input':
            return self.input(websocket, message)
        else:
            raise HandlerError('type invalid')

    async def connect(self, websocket, message):
        try:
            user_type = message['user_type']
        except KeyError:
            raise HandlerError('user_type not specified')

        await self.game.leave_room_if_connected(websocket)

        room_id = await self.game \
                            .attempt_to_join_room_and_create_user(
                                websocket, user_type)

        if not room_id:
            room_id = await self.game.create_room_and_user(
                websocket, user_type)
            await self._send_to_socket(websocket,
                                       dict(type='create', room_id=room_id))

    def input(self, websocket, message):
        return self.game.update_world(websocket, message)

    def _send_to_socket(self, websocket, dct):
        return websocket.send(json.dumps(dct))
