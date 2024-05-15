import aiogram
from aiogram.filters import BaseFilter, CommandObject
from aiogram import types

from typing import Type

from django.db import models

from channels.db import database_sync_to_async

from .dispatcher import bot

from .validators import *

from .checks import *

from ..infrastructure.enums import *

from .forms.forms import UserInformStatesGroup

from static_text.chat_messages import *
from static_text.logging_messages import *
from logging_native.utilis.frame_log_track.frame_log_track import log_track_frame
from .logger import handlers_logger

import re


logger = handlers_logger

untracked_data = {
    'bot'
}


class RegisteredExternalIdFilter(BaseFilter):
    key = "in_db"

    def __init__(self, model: Type[models.Model], use_chat_id: bool = False):
        self.model = model
        self.use_chat_id = use_chat_id

    @log_track_frame('filter_registered_external_id', untracked_data=untracked_data)
    async def __call__(self, message: types.Message, command: CommandObject, *args, **kwargs) -> bool: #TODO: consider swapping operating
    #TODO:                                                                      a message to operating a telegram object
        logger.info("")

        if self.use_chat_id:
            id_ = message.chat.id
        else:
            id_ = message.from_user.id
        model_object_attributes={'external_id': id_}

        @database_sync_to_async
        def on_id_object_exists(): #TODO: consider moving to checks.py
            return self.model.objects.filter(external_id=id_).exists()

        if self.model == Profile: #match-case statement does not work due to name capturing
            if await on_id_object_exists()\
                    and (mode:=command.args) != RegistrationMode.REREGISTER.value\
                    and mode != RegistrationMode.DELETE.value: #TODO: use in instead
                logger.error(
                    profile_is_not_registered_by_attributes_check_fail_logging_error_message.format(
                        profile_attributes=model_object_attributes
                    )
                )
                await message.answer(
                    profile_is_not_registered_by_attributes_check_fail_chat_error_message.format(
                        profile_attributes=external_id_kwc
                    )
                )

                return False

            logger.error(
                profile_is_not_registered_by_attributes_check_success_logging_info_message.format(
                    profile_attributes=model_object_attributes
                )
            )

        if self.model == Journal:
            if await on_id_object_exists() \
                    and (mode := command.args) != RegistrationMode.REREGISTER.value \
                    and mode != RegistrationMode.DELETE.value:  # TODO: use in instead
                logger.error(
                    journal_is_not_registered_by_attributes_check_fail_logging_error_message.format(
                        journal_attributes=model_object_attributes
                    )
                )
                await message.answer(
                    journal_is_not_registered_by_attributes_check_fail_chat_error_message.format(
                        journal_attributes=external_id_kwc
                    )
                )

                return False

            logger.error(
                journal_is_not_registered_by_attributes_check_success_logging_info_message.format(
                    journal_attributes=model_object_attributes
                )
            )

        return True

class IsAdminFilter(BaseFilter): #TODO: add a middleware to check both is admin or is superuser rights when is admin checking
    key = 'is_admin'
    required_auth_level = 'administrator'
    creator = 'creator'

    @log_track_frame('filter_is_admin', untracked_data=untracked_data)
    async def __call__(self, message: types.Message, *args, **kwargs) -> bool:
        logger.info("")
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        member = await bot.get_chat_member(chat_id, user_id)
        is_admin = member.status == self.required_auth_level or member.status == self.creator

        if is_admin:
            return True

        else:
            await message.answer(is_superuser_check_fail_chat_error_message)
            return False

class IsSuperUserFilter(BaseFilter):
    @log_track_frame('filter_is_superuser', untracked_data=untracked_data)
    async def __call__(self, message: types.Message, *args, **kwargs) -> bool:
        logger.info("")

        user_id = message.from_user.id

        if await is_superuser(user_id):
            return True

        else:
            await message.answer(is_superuser_check_fail_chat_error_message)
            logging.error(is_superuser_check_fail_logging_error_message)
            return False


class SuperuserCalledUserToDELETEFilter(BaseFilter):
    @log_track_frame('filter_super_user_called_user_to_delete', untracked_data=untracked_data)
    async def __call__(self, message: types.Message, command: CommandObject, state: FSMContext, *args, **kwargs):
        logger.info("")

        user_id = message.from_user.id

        if await is_superuser(user_id):

            if (mode:=command.args) == RegistrationMode.DELETE.value:
                if await state.get_state() == UserInformStatesGroup.receiver_id.state and await state.get_data():
                    return True

                else:
                    await message.answer(profile_is_applied_to_check_fail_chat_error_message)
                    logger.error(profile_is_applied_to_check_fail_logging_error_message)

            else:
                return True

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


class AftercommandFullCheck(BaseFilter): #TODO: pass all arguments to middleware to handler #TODO: configure for multiple flags usage
    key = 'aftercommand'

    def __init__(self, allow_no_argument: bool, modes: Enum=None, mode_checking: bool=False, allow_no_mode: bool=False,
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

    @log_track_frame('filter_aftercommand_full_check', untracked_data=untracked_data)
    async def __call__(self, message: types.Message, command: CommandObject, *args, **kwargs) -> bool:
        logger.info("")

        aftercommand = command.args

        try:
            aftercommand_check(aftercommand)
        except:
            if self.allow_no_argument:
                return True

            logger.error(arguments_pass_check_fail_logging_error_message)
            await message.answer(arguments_pass_check_fail_chat_error_message)
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
            try:
                pseudo_mode
                logger.info(
                    mode_pass_check_success_logging_error_message.format(arguments=arguments)
                )
            except:
                logger.info(
                    mode_pass_check_fail_logging_error_message.format(arguments=arguments)
                )
                await message.answer(mode_pass_check_fail_chat_error_message)
                return False

            try:
                validate_is_mode(pseudo_mode, self.modes)
            except:

                if self.allow_no_mode:
                    try:
                        self.additional_arguments_checker.validation_function(pseudo_mode)
                        additional_argument = pseudo_mode
                        additional_arguments.insert(0, additional_argument)

                    except:
                        await message.answer(mode_validation_fail_chat_error_message)
                        return False
                else:
                    logger.info(mode_pass_check_fail_logging_error_message.format(arguments=arguments))
                    await message.answer(mode_pass_check_fail_chat_error_message) #TODO: check
                    return False

        if self.flag_checking: #TODO: add separate flag validator, implement it
            try:
                validate_is_mode(pseudo_flag, self.modes.Flag)
            except:
                try:
                    self.additional_arguments_checker.validation_function(pseudo_flag)
                    additional_argument = pseudo_flag
                    additional_arguments.append(additional_argument)

                except:
                    await message.answer(flag_validation_fail_chat_error_message)
                    return False

        if self.additional_arguments_checker:
            if not additional_arguments:
                logger.error(
                    self.additional_arguments_checker.validation_fail_logging_error_message.format(
                        arguments=additional_arguments
                    )
                )
                await message.answer(self.additional_arguments_checker.validation_fail_chat_error_message)
                return False

            try:
                for argument in additional_arguments:
                    self.additional_arguments_checker.validation_function(argument)
                logger.info(
                    self.additional_arguments_checker.validation_success_logging_info_message.format(
                        arguments=additional_arguments
                    )
                )
            except:
                logger.error(
                    self.additional_arguments_checker.validation_fail_logging_error_message.format(
                        arguments=additional_arguments
                    )
                )
                await message.answer(self.additional_arguments_checker.validation_fail_chat_error_message)
                return False

        return True


class NoCommandFilter(BaseFilter):
    @log_track_frame('filter_no_command', untracked_data=untracked_data)
    async def __call__(self, message: types.Message, *args, **kwargs) -> bool:
        logger.info("")

        command_pattern_compiled = re.compile('\/.*')

        return not command_pattern_compiled.fullmatch(message.text)


class PresencePollFilter(BaseFilter):
    @log_track_frame('filter_presence_poll', untracked_data=untracked_data)
    async def __call__(self, poll_answer: types.PollAnswer, *args, **kwargs) -> bool:
        logger.info("")

        return await is_presence_poll(poll_answer.poll_id)