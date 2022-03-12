from typing import Dict, List
from enum import Enum
from abc import ABCMeta
from dataclasses import dataclass, field

EVENT_TYPE_KEY = 'type'
NOTICE_TYPE_KEY = 'type'


Event = Dict
Notice = Dict
RouterResponse = List[Notice]


class EventType(Enum):
    ECHO = 'echo'


class NoticeType(Enum):
    ERROR = 'error'
    ECHO = 'echo'


class NoticeErrorCode(Enum):
    pass


class RoutingLayerError(RuntimeError):
    pass


class EventNotSupported(RoutingLayerError):
    def __init__(self, event: Event):
        event_string = str(event)
        message = f'Unsupported event: {event_string}'
        super().__init__(message)


@dataclass(init=True, frozen=True)
class ValidationResult:
    valid: bool
    errors: List[Notice] = field(default_factory=list)


class EventHandler(metaclass=ABCMeta):
    def supports(self, event: Event) -> bool:
        raise NotImplemented

    def validate(self, event: Event) -> ValidationResult:
        raise NotImplemented

    def handle(self, event: Event) -> List[Notice]:
        raise NotImplemented


class EchoEventHandler(EventHandler):
    def supports(self, event: Event) -> bool:
        return event[EVENT_TYPE_KEY] == EventType.ECHO.value

    def validate(self, event: Event) -> ValidationResult:
        return ValidationResult(valid=True)

    def handle(self, event: Event) -> List[Notice]:
        return [event, ]


class EventRouter:
    def __init__(self):
        self._handlers: List[EventHandler] = list()

    def route(self, event: Event) -> RouterResponse:
        response = list()
        for handler in self._handlers:
            if handler.supports(event):
                validation = handler.validate(event)
                if validation.valid:
                    handler_response = handler.handle(event)
                    response += handler_response
                response += validation.errors
                return response
        raise EventNotSupported(event)

    def add_handler(self, handler: EventHandler) -> 'EventRouter':
        self._handlers.append(handler)
        return self


def configure_event_router() -> EventRouter:
    router = EventRouter().add_handler(EchoEventHandler())
    return router
