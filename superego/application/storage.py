from abc import ABCMeta, abstractmethod
from typing import List, Dict
from uuid import UUID

from superego.game.game import Card


class CardStorage(metaclass=ABCMeta):
    @abstractmethod
    def store(self, card: Card) -> None:
        raise NotImplemented

    @abstractmethod
    def get_all(self) -> List[Card]:
        raise NotImplemented


class PersonStorage(metaclass=ABCMeta):
    @abstractmethod
    def store(self, name: str) -> None:
        raise NotImplemented

    @abstractmethod
    def retrieve_guid(self, name: str) -> UUID:
        raise NotImplemented

    @abstractmethod
    def retrieve_all(self) -> Dict[str, UUID]:
        raise NotImplemented