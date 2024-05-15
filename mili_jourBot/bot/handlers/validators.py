#TODO: rename file
import logging

from django.core.exceptions import ValidationError

from channels.db import database_sync_to_async

from aenum import Enum

from ..infrastructure.enums import *

from static_text import chat_messages
from static_text.chat_messages import *
from static_text import logging_messages
from static_text.logging_messages import *

from ..db_actions import on_lesson_presence_check

from ..models import Journal, Superuser, PresencePoll, Profile

from .forms.forms import SetJournalStatesGroup

from misc.re_patterns import *

from aiogram.fsm.context import FSMContext

import regex



def aftercommand_check(value): #TODO: pass a command object instead
    if value:
        return True

    raise ValidationError(arguments_pass_check_fail_logging_error_message.format(arguments=value), code=arguments_kw)


def validate_is_mode(value, modes: Enum):

    mode = next((mode for mode in modes if mode.value == value), None)

    if mode:
        return  True

    raise ValidationError(mode_validation_fail_chat_error_message.format(mode=value), code=arguments_kw)


 #TODO: add separate flag validator, implement it


class AdditionalArgumentsValidator:
    def __init__(
            self,
            validation_function                     ,
            validation_fail_chat_error_message      ,
            validation_fail_logging_error_message   ,
            validation_success_logging_info_message ,
    ):
        self.validation_function = validation_function
        self.validation_fail_chat_error_message = validation_fail_chat_error_message
        self.validation_fail_logging_error_message = validation_fail_logging_error_message
        self.validation_success_logging_info_message = validation_success_logging_info_message

def validate_lesson(value):
    try:
        value_integer = int(value)

    except Exception as e:
        logging.exception("", exc_info=True)
        raise ValidationError(
            lessons_pass_check_fail_logging_error_message.format(
                arguments=value
            )
            ,
            code=arguments_kw
        )

    if value_integer in Schedule.lessons_intervals.keys():
        return True

    else:
        raise ValidationError(lessons_pass_check_fail_logging_error_message.format(arguments=value), code=arguments_kw)

lessons_validator = AdditionalArgumentsValidator(
    validate_lesson                                 ,
    lessons_pass_check_fail_chat_error_message      ,
    lessons_pass_check_fail_logging_error_message   ,
    lessons_pass_check_success_logging_info_message ,
)


class NativeDateFormat:
    date_format = '%d.%m.%Y' #TODO: move date format to separate file

def validate_date_format(value):
    date_format = NativeDateFormat.date_format

    try:
        datetime.datetime.strptime(value, date_format).date()
        return

    except:
        raise ValidationError(date_format_validation_fail_logging_error_message.format(arguments=value), code='format')

date_validator = AdditionalArgumentsValidator(
    validate_date_format                         ,
    date_pass_check_fail_chat_error_message      ,
    date_pass_check_fail_logging_error_message   ,
    date_pass_check_success_logging_info_message ,
)


async def validate_during_lesson_presence(user_id): #TODO: rename to "validate_during_lesson_presence
    try:
        await on_lesson_presence_check(user_id)
        #TODO: return true
    except:
        raise ValidationError(during_lesson_check_fail_logging_error_message.format(arguments=user_id), code=presence_kw)


def validate_report_format(value: str):

    if not regex.fullmatch(pattern=report_rePattern, string=value):

        raise ValidationError(
            report_table_format_validation_fail_logging_error_message.format(arguments=value),
            code='regex_match'
        )

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
        raise ValidationError(report_table_name_references_validation_fail_logging_error_message.format(arguments=value), code=profile_name_kws + references)

    else:
        return True


@database_sync_to_async
def validate_journal_is_registered(**journal_attributes):
    try:
        journal = Journal.objects.get(**journal_attributes)

    except Journal.DoesNotExist:

        raise ValidationError(
            journal_is_registered_by_attributes_check_fail_logging_error_message.format(
                journal_attributes=journal_attributes
            )
        )