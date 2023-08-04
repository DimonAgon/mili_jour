
import logging

from django.core.exceptions import ValidationError

from aenum import Enum

from ..infrastructure.enums import *

from .static_text import *

from ..views import on_lesson_presence_check


def aftercommand_check(value):
    if value:
        return True

    raise ValidationError("Command initiation failed\nError: no arguments", code='arguments')


def validate_is_mode(value, modes: Enum):

    mode = next((mode for mode in modes if mode.value == value), None)

    if mode:
        return  True

    raise ValidationError(f"Command initiation failed\nError:no such mode \"{value}\"", code='arguments')


class AdditionalArgumentsValidator:
    def __init__(self, validation_function, validation_error_message):
        self.validation_function = validation_function
        self.validation_error_message = validation_error_message

def validate_lesson(value):
    try:
        value_integer = int(value)

    except Exception as e:
        raise ValidationError(f"Command initiation failed\nError:{e}", code='arguments')

    if value_integer in Schedule.lessons_intervals.keys():
        return True

    else:
        raise ValidationError("Command initiation failed\nError: wrong lesson arguments", code='arguments')

lessons_validator = AdditionalArgumentsValidator(validate_lesson, wrong_lessons_validation_error_mesage)



class NativeDateFormat:
    date_format = '%d.%m.%Y'

def validate_date_format(value):
    date_format = NativeDateFormat.date_format

    try:
        datetime.datetime.strptime(value, date_format).date()
        return

    except:
        raise ValidationError("wrong date format", code='format')

date_validator = AdditionalArgumentsValidator(validate_date_format, wrong_date_validation_error_message)


async def validate_on_lesson_presence(user_id):
    try:
        await on_lesson_presence_check(user_id)

    except:
        logging.error(f"failed to set a status for user {user_id}, lesson is None")
        return