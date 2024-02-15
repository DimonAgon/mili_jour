import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext

from typing import Any, Awaitable, Callable, Dict

from channels.db import database_sync_to_async

from ..models import *
from .validators import *
from ..forms import *
from ..db_actions import *

from django.core.exceptions import ValidationError



class SuperuserSetJournal(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:

        user_id = event.from_user.id
        if event.chat.type == 'private':
            state = data['state']
            if await check_journal_set(state):
                set_journal_name = (await state.get_data())['set_journal_name']
                set_journal = await get_journal_by_name_async(set_journal_name)
                set_journal_external_id = set_journal.external_id
                data['set_journal_group_id'] = set_journal_external_id

            else:
                logging.error(no_journal_set_error_message.format(user_id))
                await event.answer(no_journal_set_message)
                return


        return await handler(event, data)


class ApplyArguments(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:

        try:
            arguments = data['command'].args.split()

        except Exception:
            return await handler(event, data)

        pseudo_mode = arguments[0]

        for modes in all_modes:
            try:
                validate_is_mode(pseudo_mode, modes)
                mode = pseudo_mode
                data['mode'] = mode
                break

            except ValidationError:
                continue

        else:
            mode = None

        pseudo_flag = arguments[-1]

        if mode:
            try:
                validate_is_mode(pseudo_flag, modes.Flag)
                flag = pseudo_flag
                data['flag'] = flag

            except Exception:
                flag = None

        else:
            for modes in all_modes:
                try:
                    validate_is_mode(pseudo_flag, modes.Flag)
                    flag = pseudo_flag
                    data['flag'] = flag
                    break

                except Exception:
                    continue

            else:
                flag = None

        additional_arguments = tuple(set(arguments) - set((mode, flag)))

        if additional_arguments:
            data['additional_arguments'] = additional_arguments

        return await handler(event, data)



#TODO: add superuser HELP










