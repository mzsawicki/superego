import json
from datetime import datetime
from typing import Dict
from uuid import UUID

from dataclasses_serialization.serializer_base import\
    noop_serialization,\
    dict_serialization,\
    Serializer

from superego.game.game import GamePhaseName, GameState
from superego.infrastructure.websockets.feedback import Feedback, Status
from superego.infrastructure.websockets.events import EventAction, Event
from superego.infrastructure.time import TimeProvider


class DeserializationError(RuntimeError):
    pass


class UnknownEventAction(DeserializationError):
    def __init__(self, action_name: str):
        message = f'Event action unknown: {action_name}'
        super().__init__(message)


def _serialize_datetime(datetime_: datetime) -> str:
    text = datetime_.strftime('%m/%d/%y %H:%M:%S')
    return text


def _serialize_game_phase_name(game_phase_name: GamePhaseName) -> str:
    value = game_phase_name.value
    return value


def _serialize_uuid(uuid: UUID) -> str:
    text = str(uuid)
    return text


def _serialize_feedback_status(status: Status) -> str:
    value = status.value
    return value


JSONSerializer = Serializer(
    serialization_functions={
        dict: lambda dct: dict_serialization(
            dct, key_serialization_func=JSONSerializer.serialize,
            value_serialization_func=JSONSerializer.serialize),
        list: lambda lst: list(map(JSONSerializer.serialize, lst)),
        (str, int, float, bool, type(None)): noop_serialization,
        datetime: _serialize_datetime,
        GamePhaseName: _serialize_game_phase_name,
        UUID: _serialize_uuid,
        Status: _serialize_feedback_status

    },
    deserialization_functions={}
)


def serialize_game_state(game_state: GameState) -> str:
    feedback = Feedback(status=Status.GAME_STATE, data=game_state)
    json_ = JSONSerializer.serialize(feedback)
    string = json.dumps(json_)
    return string


def serialize_confirmation() -> str:
    feedback = Feedback(status=Status.ACKNOWLEDGED, data=None)
    json_ = JSONSerializer.serialize(feedback)
    string = json.dumps(json_)
    return string


def deserialize_json(message: str) -> Dict:
    dict_ = json.loads(message)
    return dict_


def deserialize_event(event_dict: Dict, time_provider: TimeProvider) -> Event:
    params = event_dict['params'] if 'params' in event_dict else list()
    time_received = time_provider.now()
    issuer = _deserialize_issuer(event_dict['issuer'])
    action = _deserialize_event_action(event_dict['action'])

    event = Event(
        time_received=time_received,
        issuer=issuer,
        action=action,
        params=params
    )

    return event


def _deserialize_issuer(issuer_text: str) -> UUID:
    return UUID(issuer_text)


def _deserialize_event_action(action_text: str) -> EventAction:
    if action_text == EventAction.GUESS.value:
        return EventAction.GUESS
    elif action_text == EventAction.ANSWER.value:
        return EventAction.ANSWER
    elif action_text == EventAction.CHANGE_CARD.value:
        return EventAction.CHANGE_CARD
    elif action_text == EventAction.SUBSCRIBE.value:
        return EventAction.SUBSCRIBE
    elif action_text == EventAction.READ.value:
        return EventAction.READ
    else:
        raise UnknownEventAction(action_text)
