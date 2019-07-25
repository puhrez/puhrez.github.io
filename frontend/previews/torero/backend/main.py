#!/usr/bin/env python
import asyncio
import websockets
from game import Game
from websocket_api import ToroWebSocketAPI


if __name__ == '__main__':
    socket_api = ToroWebSocketAPI(Game())

    start_server = websockets.serve(socket_api.main, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
