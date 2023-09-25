import aiogram
from aiogram.filters import BaseFilter, CommandObject
from aiogram import types

from typing import Type

from django.db import models

from channels.db import database_sync_to_async

from .dispatcher import bot

from .validators import *

from ..infrastructure.enums import *

from ..forms import UserInformStatesGroup

import logging

import re


class RegisteredExternalIdFilter(BaseFilter):
    key = "in_db"

    def __init__(self, model: Type[models.Model], use_chat_id: bool = False):
        self.model = model
        self.use_chat_id = use_chat_id

    async def __call__(self, message: types.Message, command: CommandObject) -> bool:
        @database_sync_to_async
        def on_id_object_exists():
            if self.use_chat_id:
                id_ = message.chat.id
            else:
                id_ = message.from_user.id
            return self.model.objects.filter(external_id=id_).exists()

        if await on_id_object_exists()\
                and (mode:=command.args) != RegistrationMode.REREGISTER.value\
                and mode != RegistrationMode.DELETE.value:
            if self.use_chat_id:
                await message.answer(on_id_model_object_exists_error_message_to_group)
                logging.error(on_id_model_object_exists_logging_error_message_to_group.format(message.chat.id))

            else:
                await message.answer(on_id_model_object_exists_error_message_to_user)
                logging.error(on_id_model_object_exists_logging_error_to_user.format(message.from_user.id))

            return False

        return True

class IsAdminFilter(BaseFilter): #TODO: add a middleware to check both is admin or is superuser rights when is admin checking
    key = 'is_admin'
    required_auth_level = 'administrator'
    creator = 'creator'

    async def __call__(self, message: types.Message) -> bool:
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        member = await bot.get_chat_member(chat_id, user_id)
        is_admin = member.status == self.required_auth_level or member.status == self.creator

        return is_admin

class IsSuperUserFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:

        user_id = message.from_user.id

        if await is_superuser(user_id):
                return True

        else:
            logging.error(user_unauthorised_as_superuser_logging_info_message.format(user_id))
            message.answer(user_unauthorised_as_superuser_message) #TODO: fix, add await
            return False


class SuperUserCalledUserToDELETEFilter(BaseFilter):
    async def __call__(self, message: types.Message, command: CommandObject, state: FSMContext):

        user_id = message.from_user.id

        if await is_superuser(user_id):

            if (mode:=command.args) == RegistrationMode.DELETE.value:
                if await state.get_state() == UserInformStatesGroup.receiver_id.state and await state.get_data():
                    return True

                else:
                    await message.answer(user_not_called_text)
                    logging.error(no_user_called_logging_error_message.format(user_id))

        else:
            return True

#TODO: in case of dialoging via call
# class IsNowSpeaking(BaseFilter):
#     async def __call__(self, message: types.Message, state: FSMContext) -> bool:
#
#         user_id = message.from_user.id
#         interlocutor_id = await state.get_data()
#
#         if not interlocutor_id['Interlocutor_id'] == user_id:
#             return True
#
#         else:
#             logging.error(f"interlocution message from user {user_id} was not sent, user is now listening")
#             await message.answer(is_not_now_speaking_error_message)
#             return False


class AftercommandFullCheck(BaseFilter): #TODO: pass all arguments to middleware to handler
    key = 'aftercommand'

    def __init__(self, allow_no_argument: bool, modes: Enum, mode_checking: bool=False, allow_no_mode: bool=False,
                 additional_arguments_checker: Type[AdditionalArgumentsValidator]=None,
                 flag_checking=False):
        """
        :param allow_no_mode: Specify if mode checking is True. By default is set False
        """
        self.allow_no_argument = allow_no_argument
        self.allow_no_mode = allow_no_mode
        self.modes = modes
        self.mode_checking = mode_checking
        self.additional_arguments_checker = additional_arguments_checker
        self.flag_checking = flag_checking
    async def __call__(self, message: types.Message, command: CommandObject) -> bool:
        aftercommand = command.args

        try: aftercommand_check(aftercommand)
        except:
            if self.allow_no_argument:
                return True

            await message.answer(no_arguments_validation_error_message)
            return False

        arguments = aftercommand.split()

        if self.mode_checking and self.additional_arguments_checker and self.flag_checking:
            pseudo_mode, *additional_arguments, pseudo_flag = arguments

        elif self.mode_checking and self.additional_arguments_checker:
            pseudo_mode, *additional_arguments = arguments

        elif self.mode_checking and self.flag_checking:
            pseudo_mode, pseudo_flag = arguments

        elif self.additional_arguments_checker and self.flag_checking:
            *additional_arguments, pseudo_flag = arguments

        elif self.mode_checking:
            pseudo_mode = arguments[0]

        elif self.additional_arguments_checker:
            additional_arguments = arguments

        elif self.flag_checking:
            pseudo_flag = arguments[0]

        if self.mode_checking:
            try: pseudo_mode
            except:
                await message.answer(no_mode_validation_error_message)
                return False

            try: validate_is_mode(pseudo_mode, self.modes)
            except:

                if self.allow_no_mode:
                    try:
                        self.additional_arguments_checker.validation_function(pseudo_mode)
                        additional_argument = pseudo_mode
                        additional_arguments.insert(0, additional_argument)

                    except:
                        await message.answer(wrong_mode_validation_error_message)
                        return False
                else:
                    await message.answer(wrong_mode_validation_error_message)
                    return False

        if self.flag_checking:
            try: validate_is_mode(pseudo_flag, self.modes.Flag)
            except:
                try:
                    self.additional_arguments_checker.validation_function(pseudo_flag)
                    additional_argument = pseudo_flag
                    additional_arguments.append(additional_argument)

                except:
                    await message.answer(wrong_mode_validation_error_message)
                    return False

        if self.additional_arguments_checker:
            if not additional_arguments:
                await message.answer(self.additional_arguments_checker.validation_error_message)
                return False

            try:
                for i in additional_arguments:
                    self.additional_arguments_checker.validation_function(i)
            except:
                await message.answer(self.additional_arguments_checker.validation_error_message)
                return False

        return True


class NoCommandFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        command_pattern_compiled = re.compile('\/.*')

        return not command_pattern_compiled.fullmatch(message.text)


class PresencePollFilter(BaseFilter):
    async def __call__(self, poll_answer: types.PollAnswer) -> bool:

        return await is_presence_poll(poll_answer.poll_id)