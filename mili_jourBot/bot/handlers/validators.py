
import logging

from django.core.exceptions import ValidationError

from channels.db import database_sync_to_async

from aenum import Enum

from ..infrastructure.enums import *

from .static_text import *

from ..db_actions import on_lesson_presence_check

from ..models import Journal, Superuser, PresencePoll, Profile

from ..forms import SetJournalStatesGroup

from misc.re_patterns import *

from aiogram.fsm.context import FSMContext

import regex



def aftercommand_check(value): #TODO: pass a command object instead
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


async def validate_on_lesson_presence(user_id): #TODO: check
    try:
        await on_lesson_presence_check(user_id)

    except:
        raise ValidationError(f"failed to set a status for user {user_id}, lesson is None", code='presence check')
    #  TODO: move string to static_text.py


def validate_report_format(value: str):

    if not regex.fullmatch(pattern=report_rePattern, string=value):

        raise ValidationError("report foramt validation failed", code='regex_match')

    else:
        return True


@database_sync_to_async
def validate_report_name_references(value: str, journal):
    names_matches = regex.finditer(f"{full_name_rePattern}|{name_rePattern}", value) #order inside pattern matters
    names = [match.group() for match in names_matches]
    names.remove("Студент")
    journal_profiles = Profile.objects.filter(journal=journal)
    referred_profiles = [profile for profile in journal_profiles if any(name in profile.name for name in names)]

    if not len(names) == len(referred_profiles):
        raise ValidationError("report name references validation failed", code='name references check')

    else:
        return True


async def check_journal_set(state: FSMContext):
    return await state.get_state() == SetJournalStatesGroup.set_journal


@database_sync_to_async
def is_superuser(user_id):
    return Superuser.objects.filter(external_id=user_id).exists()


@database_sync_to_async
def is_presence_poll(poll_id):
    return PresencePoll.objects.filter(external_id=poll_id).exists()
