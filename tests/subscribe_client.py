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
            'issuer': 'a7da476f-c81b-4bc7-ac17-e7e675ccc95f'
        }
        message = json.dumps(dict_)
        data = message.encode(ENCODING)
        await websocket.send(data)
        response = await websocket.recv()
        print(response)
        dict_ = {
            'action': 'READ',
            'issuer': 'a7da476f-c81b-4bc7-ac17-e7e675ccc95f'
        }
        message = json.dumps(dict_)
        data = message.encode(ENCODING)
        await websocket.send(data)
        response = await websocket.recv()
        print(response)


if __name__ == '__main__':
    asyncio.run(listen(f'ws://{SERVER_HOST}:{SERVER_PORT}'))
