from abc import ABCMeta, abstractmethod
from datetime import datetime

from superego.game.game import Clock


class TimeProvider(metaclass=ABCMeta):
    @abstractmethod
    def now(self) -> datetime:
        raise NotImplemented


class SimpleLocalTimeProvider(TimeProvider):
    def now(self) -> datetime:
        return datetime.now()


class TimeProviderClock(Clock):
    def __init__(self, time_provider: TimeProvider):
        self._time_provider: TimeProvider = time_provider

    def now(self) -> datetime:
        return self._time_provider.now()
