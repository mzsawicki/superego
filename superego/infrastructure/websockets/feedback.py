from enum import Enum
from typing import Any
from dataclasses import dataclass


class Status(Enum):
    ACKNOWLEDGED = 'ACK'
    ERROR = 'ERR'
    GAME_STATE = 'STAT'


@dataclass(init=True, frozen=True)
class Feedback:
    status: Status
    data: Any
