import asyncio
import json

from websockets import connect

ENCODING = 'utf-8'

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000


async def listen(uri):
    async with connect(uri) as websocket:
        dict_ = {
            'action': 'SUBSCRIBE',
            'issuer': '55ae1d15-3aa1-4277-90e1-fd711aad6d0d'
        }
        message = json.dumps(dict_)
        data = message.encode(ENCODING)
        await websocket.send(data)
        response = await websocket.recv()
        print(response)
        dict_ = {
            'action': 'READ',
            'issuer': '55ae1d15-3aa1-4277-90e1-fd711aad6d0d'
        }
        message = json.dumps(dict_)
        data = message.encode(ENCODING)
        await websocket.send(data)
        response = await websocket.recv()
        print(response)


if __name__ == '__main__':
    asyncio.run(listen(f'ws://{SERVER_HOST}:{SERVER_PORT}'))
