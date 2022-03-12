import asyncio
from websockets import connect
import json

ENCODING = 'utf-8'

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000


async def echo(uri):
    async with connect(uri) as websocket:
        event = {'type': 'echo'}
        json_ = json.dumps(event)
        message = str(json_)
        data = message.encode(ENCODING)
        await websocket.send(data)
        response_data = await websocket.recv()
        response_message = response_data.decode(ENCODING)
        notice = json.loads(response_message)
        print(notice)


if __name__ == '__main__':
    asyncio.run(echo(f'ws://{SERVER_HOST}:{SERVER_PORT}'))
