
from channels.db import database_sync_to_async

from ..models import *
from static_text.chat_messages import *
from static_text.logging_messages import *
from .forms.forms import *

from aiogram.fsm.context import FSMContext

import logging


async def check_journal_set(state: FSMContext):

    journal_set = (await state.get_data())['set_journal']
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