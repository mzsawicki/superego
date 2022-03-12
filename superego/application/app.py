from abc import ABCMeta, abstractmethod


class Server(metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> None:
        raise NotImplemented


class App:
    def __init__(self, game_server: Server):
        self._game_server: Server = game_server

    def start(self):
        self._game_server.run()


