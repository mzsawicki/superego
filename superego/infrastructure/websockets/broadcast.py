import asyncio
from abc import ABCMeta, abstractmethod
from typing import List

import websockets
from websockets import WebSocketServerProtocol


class Broadcast(metaclass=ABCMeta):
    @abstractmethod
    async def add_listener(self, websocket: WebSocketServerProtocol) -> None:
        raise NotImplemented

    @abstractmethod
    def broadcast(self, message: str) -> None:
        raise NotImplemented


class WebSocketsBroadcast(Broadcast):
    def __init__(self):
        self._listeners: List[WebSocketServerProtocol] = list()

    async def add_listener(self, websocket: WebSocketServerProtocol) -> None:
        self._listeners.append(websocket)

    def broadcast(self, message: str) -> None:
        websockets.broadcast(self._listeners, message)
