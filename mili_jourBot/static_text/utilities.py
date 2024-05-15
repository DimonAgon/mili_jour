
from .logging_messages import *
from .chat_messages import *


def chat_field_message_to_logging_field_message(chat_field_message: str) -> str:
    logging_field_message = chat_field_message.replace("chat", "logging")
    return globals().get(logging_field_message)


def presence_option_to_string(presence_option: Type[PresencePollOptions]):
    match presence_option:
        case PresencePollOptions.Present:
            return "Я"
        case PresencePollOptions.Absent:
            return "Відсутній"