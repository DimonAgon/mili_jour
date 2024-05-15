from .logger import handlers_logger

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext

from typing import Any, Awaitable, Callable, Dict

from channels.db import database_sync_to_async

from ..models import *
from .validators import *
from .checks import *
from ..forms import *
from ..db_actions import *
from logging_native.utilis.frame_log_track.frame_log_track import log_track_frame

from django.core.exceptions import ValidationError


logger = handlers_logger

#TODO: annotate return types for all of the middleware

class SuperuserSetJournal(BaseMiddleware):
    @log_track_frame('superuser_set')
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:

        if event.chat.type == 'private':
            state = data['state']
            if await check_journal_set(state):
                set_journal = (await state.get_data())['set_journal']
                data['set_journal'] = set_journal

            else:
                await event.answer(journal_set_check_fail_chat_error_message)
                return


        return await handler(event, data)


class ApplyArguments(BaseMiddleware): #TODO: configure for multiple flags usage
    @log_track_frame('apply_arguments')
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


def get_chat_identifying_attributes_from_event(event: TelegramObject) -> dict:
    chat_attributes = {}
    try:
        chat = event.chat
        chat_attributes['id'] = chat.id
        chat_attributes['type'] = chat.type
        chat_attributes['title'] = chat.title

    except Exception:
        logger.exception("", exc_info=True)

    return chat_attributes

def get_user_identifying_attributes_from_event(event: TelegramObject) -> dict:
    user_attributes = {}
    if isinstance(event, Message):
        user = event.from_user

    else:
        try:
            user = event.user

        except AttributeError:
            user = None

        finally:
            logger.exception("", exc_info=True)

    if user:
        user_attributes['id'] = user.id
        user_attributes['first_name'] = user.first_name
        user_attributes['last_name'] = user.last_name
        user_attributes['username'] = user.username

    return user_attributes

def get_user_credentials(event: TelegramObject) -> dict:
    user_identifying_attributes = get_user_identifying_attributes_from_event(event)
    user_credentials = user_identifying_attributes

    profile_attributes = {'external_id': user_identifying_attributes['id']}
    try:
        user_profile = Profile.objects.get(**profile_attributes)

    except Profile.DoesNotExist:
        pass

    except Exception:
        logger.exception(
            profile_existence_check_fail_logging_error_message.format(profile_attributes=profile_attributes)
        )
        return user_credentials

    try:
        user_profile
        logger.info(
            profile_existence_check_success_logging_info_message.format(profile_attributes=profile_attributes)
        )
        user_credentials['profile_id'] = user_profile.id
        user_credentials['profile_name'] = user_profile.name
        user_credentials['ordinal'] = user_profile.ordinal
    except NameError:
        ...

    return user_credentials

def get_chat_credentials(event: TelegramObject) -> dict:
    chat_identifying_attributes = get_chat_identifying_attributes_from_event(event)
    chat_credentials = chat_identifying_attributes
    journal_attributes = {'external_id': chat_identifying_attributes['id']}
    try:
        chat_journal = Journal.objects.get(**journal_attributes)

    except Journal.DoesNotExist:
        pass

    except Exception:
        logger.exception(
            journal_existence_check_fail_logging_error_message.format(journal_attributes=journal_attributes),
            exc_info=True
        )

        return chat_credentials

    try:
        chat_journal
        logger.info(
            journal_existence_check_success_logging_info_message.format(journal_attributes=journal_attributes),
        )
        chat_credentials['journal_id'] = chat_journal.id
        chat_credentials['journal_name'] = chat_journal.name
    except NameError:
        ...

    return chat_credentials



class PassUserCredentials(BaseMiddleware):
    @log_track_frame('pass_user_credentials')
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        try:
            user_credentials = get_user_credentials(event)

        except Exception:
            logger.exception("", exc_info=True)
            return await handler(event, data)

        data['user_credentials'] = user_credentials

        return await handler(event, data)


class PassChatCredentials(BaseMiddleware):
    @log_track_frame('pass_chat_credentials')
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        try:
            chat_credentials = get_chat_credentials(event)

        except Exception:
            logger.exception('', exc_info=True)
            return await handler(event, data)

        data['chat_credentials'] = chat_credentials

        return await handler(event, data)


class LogTrackFrame(BaseMiddleware): #TODO: fix parent frame function tracking

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ):

        await log_track_frame(untracked_data={'event'})(handler)(event, data)









