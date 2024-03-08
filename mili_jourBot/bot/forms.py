
from aiogram import types

from aiogram_forms import Form, fields, dispatcher, FormsManager
from aiogram_forms.errors import ValidationError
from aiogram.filters.state import State, StatesGroup

from channels.db import database_sync_to_async

from bot.handlers.dispatcher import bot
from .db_actions import *
from .models import *
from .handlers.static_text import *
from misc.re_patterns import *

import logging
from django.core.exceptions import ValidationError as DjangoCoreValidationError

from key_generator.key_generator import generate


#TODO: add an ordinal filter
#TODO forms: add logging errors for all the validations
def validate_name_format(value: str):

    if not regex.fullmatch(pattern=full_name_rePattern, string=value):

        raise ValidationError(name_format_validation_error_message, code='regex_match')


@database_sync_to_async
def validate_name_available(value: str):

    if Profile.objects.filter(name=value).exists():

        raise ValidationError(name_availability_validation_error_message, code='name_in_db')


def validate_journal_format(value: str):

    if not regex.fullmatch(pattern=journal_rePattern, string=value):

        raise ValidationError(journal_format_validation_error_message, code='regex_match')


@database_sync_to_async
def validate_journal_name_available(value: str):

    if Journal.objects.filter(name=value).exists():

        raise ValidationError(journal_name_availability_validation_error_message, code='name_in_db')


@database_sync_to_async
def check_journal_exists(value: str):

    if not Journal.objects.filter(name=value).exists():
        #raise ValidationError(f"no such journal: {journal_name}")
        raise ValidationError("Взвод не зареєстровано", code='name_in_db')


def validate_ordinal_format(value: str):

    if not regex.fullmatch(pattern=ordinal_rePattern, string=value):

        raise ValidationError(ordinal_format_validation_error_message, code='regex_match')


def validate_strength_format(value: str):

    if not regex.fullmatch(pattern=sterngth_rePattern, string=value):

        raise ValidationError(strength_format_validation_error_message, code='regex_match')


def validate_super_user_key(value: str, authentic_key, user_id):

    if not value == authentic_key:

        raise DjangoCoreValidationError(f"user {user_id} superuser key is unauthentic", code='superuser_key')
        #  TODO: move string to static_text.py


class UserLeftGroupException(Exception):
    pass

@dispatcher.register('profileform')
class ProfileForm(Form):
    journal = fields.TextField(journal_field_message, validators=[validate_journal_format, check_journal_exists])
    name = fields.TextField(name_field_message, validators=[validate_name_format]) # TODO: accent on order
    ordinal = fields.TextField(ordinal_field_message, validators=[validate_ordinal_format])

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(ProfileForm)
        user_id = message.from_user.id
        journal = await get_journal_by_name_async(data['journal'])
        journal_group_id = journal.external_id


        try:
            status = await bot.get_chat_member(journal_group_id, user_id)
            if status.status == 'left':
                raise UserLeftGroupException

            else:
                await add_profile(data, user_id)
                await message.answer(text=profile_form_callback_message)
                logging.info(profile_created_info_message.format(user_id))


        except Exception as e:
            await message.answer(text=on_registration_fail_text)
            logging.error(profile_creation_error_message.format(user_id, e))


@dispatcher.register('journalform')
class JournalForm(Form):
    name = fields.TextField(journal_field_message, validators=[validate_journal_format])
    strength = fields.TextField(strength_field_message, validators=[validate_strength_format])

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(JournalForm)
        group_id = message.chat.id

        try:
            await add_journal(data, group_id)
            await message.answer(text=journal_form_callback_message)
            logging.info(journal_created_info_message.format(group_id))

        except Exception as e:
            await message.answer(text=on_registration_fail_text) #Does not work, no message
            logging.error(journal_creation_error_message)


@dispatcher.register('absenceform')
class AbsenceReason(Form):
    status = fields.TextField(status_field_message)

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(AbsenceReason)
        user_id = message.from_user.id


        try:
            await set_status(data, user_id)
            await message.answer(text=absence_reason_form_сallback_text)

        except Exception as e:
            await message.answer(text=absence_reason_fail_text)
            logging.error(status_set_error_message.format(user_id, e))


class SuperuserKeyStates(StatesGroup): key = State()

class JournalRegistrationStates(StatesGroup):
    key = State()
    set_journal = State()
    mode = State()

class AbsenceReasonStates(StatesGroup): AbsenceReason = State()

class SetJournalStatesGroup(StatesGroup):
    setting_journal = State()
    set_journal = State()

class UserInformStatesGroup(StatesGroup):
    call = State()
    receiver_id = State()

class GroupInformStatesGroup(StatesGroup):
    call = State()
    receiver_id = State()

class ReportRedoStatesGroup(StatesGroup):
    redoing = State()
    date: datetime.datetime = State()