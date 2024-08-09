
from channels.db import database_sync_to_async

from ..models import *
from static_text.chat_messages import *
from static_text.logging_messages import *
from .forms.forms import *

from aiogram.fsm.context import FSMContext

import logging


async def check_journal_set(state: FSMContext):

    try:
        journal_set = bool((await state.get_data())['set_journal'])

    except KeyError:
        journal_set = False

    if journal_set:
        logging.info(journal_set_check_success_logging_info_message)

    else:
        logging.info(journal_set_check_fail_logging_error_message)

    return journal_set


@database_sync_to_async
def is_superuser(user_id): #TODO: consider function name
    is_superuser_ = Superuser.objects.filter(external_id=user_id).exists()
    if is_superuser_:
        logging.info(is_superuser_check_success_logging_info_message)

    else:
        logging.info(is_superuser_check_fail_logging_error_message)

    return is_superuser_


@database_sync_to_async
def is_presence_poll(poll_id): #TODO: consider consider name
    is_presence_poll_ = PresencePoll.objects.filter(external_id=poll_id).exists()
    poll_attributes = {'id': poll_id}
    if is_presence_poll_:
        logging.info(is_presence_poll_check_success_logging_info_message.format(poll_attributes=poll_attributes))
        return True

    logging.info(is_presence_poll_check_fail_logging_error_message.format(poll_attributes=poll_attributes))

@log_track_frame(total=False)
def check_schedule_dict_is_not_empty(lessons_ordinals_to_subjects_names: dict):
    is_empty = bool(lessons_ordinals_to_subjects_names)
    if is_empty:
        logging.error(schedule_is_not_empty_check_fail_logging_error_message)
        return True

    else:
        logging.info(
            schedule_is_not_empty_check_success_logging_error_message.format(
                schedule_attributes=lessons_ordinals_to_subjects_names
            )
        )
        return False

@log_track_frame(total=False)
@database_sync_to_async
def check_subject_is_not_created(subject_name):
    subject_attributes = {'name': subject_name}
    is_created = Subject.objects.filter(name=subject_name).exists()
    if not is_created:
        logging.info(
            subject_is_not_created_by_attributes_check_success_logging_info_message.format(
                subject_attributes=subject_attributes
            )
        )
        return True

    else:
        logging.error(
            subject_is_not_created_by_attributes_check_fail_logging_error_message.format(
                subject_attributes=subject_attributes
            )
        )
