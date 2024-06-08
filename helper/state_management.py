from nicegui import app
from enum import Enum

initial_states = dict()


class StateKey(Enum):
    DATASET = "DATASET"
    PROMPT_DATA = "PROMPT_DATA"
    SELECTED_PROMPTS = "SELECTED_PROMPTS"
    SELECTED_DATA = "SELECTED_DATA"
    SELECTED_MODEL = "SELECTED_MODEL"
    CUSTOM_DATA_TO_CITATION = "CUSTOM_DATA_TO_CITATION"


def initialize_state(key: StateKey, value, is_global=True):
    if initial_states.get(key.value) is None:
        if is_global:
            initial_states[key.value] = value
        app.storage.user[key.value] = value


def reset_states():
    for key in StateKey:
        app.storage.user[key.value] = initial_states.get(key.value, None)


def append_state(key: StateKey, value):
    if app.storage.user.get(key.value) is None:
        app.storage.user[key.value] = value
    else:
        app.storage.user[key.value].append(value)


def get_state(key: StateKey):
    return app.storage.user.get(key.value)
