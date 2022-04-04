from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID


class EventAction(Enum):
    ANSWER = 'ANSWER'
    GUESS = 'GUESS'
    CHANGE_CARD = 'CHANGE_CARD'
    SUBSCRIBE = 'SUBSCRIBE'
    READ = 'READ'


@dataclass(frozen=True, init=True)
class Event:
    time_received: datetime
    action: EventAction
    issuer: UUID
    params: List

