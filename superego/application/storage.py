from abc import ABCMeta, abstractmethod
from typing import List

from superego.game.game import Card, Deck


class CardStorage(metaclass=ABCMeta):
    @abstractmethod
    def store(self, card: Card) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Card]:
        pass