import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.fsm.context import FSMContext

from typing import Any, Awaitable, Callable, Dict

from channels.db import database_sync_to_async

from ..models import *
from .validators import *
from ..forms import *

@database_sync_to_async
def _is_superuser(user_id):
    return Superuser.objects.filter(external_id=user_id).exists()

class SuperuserGetReportCommand(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:

        set_journal_name = await FSMContext.get_data(JournalStatesGroup.journal)

        @database_sync_to_async
        def process_super_user_get_report_command():

            if event.chat.type == 'private':
                if check_journal_set():
                    set_journal = Journal.objects.get(name=set_journal_name)
                    set_journal_external_id = set_journal.external_id
                    await handler(event, data, set_journal_group_id=set_journal_external_id)
                else:
                    raise logging.error(f"no journal set for superuser {user_id}")
                    await event.answer("журнал не було відкрито")

                return await handler(event, data)

        user_id = event.from_user.id
        if _is_superuser(user_id):
            return process_super_user_get_report_command()

        return await handler(event, data)


#TODO: add superuser HELP










