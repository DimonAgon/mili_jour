
from aiogram import types

from aiogram_forms import Form, fields, dispatcher, FormsManager
from aiogram_forms.errors import ValidationError

from channels.db import database_sync_to_async

import regex, re #TODO: adapt validators to re, where possible

from .views import *
from .models import *
from .handlers.static_text import *

import logging


#TODO: add an ordinal filter
#TODO forms: add logging errors for all the validations
def validate_name_format(value: str):

    name_rePattern = "\p{Lu}\p{Ll}+\s\p{Lu}\p{Ll}+(?:[-]\p{Lu}\p{Ll}+)?" #for any language

    if not regex.fullmatch(pattern=name_rePattern, string=value):

        raise ValidationError(name_format_validation_error_message, code='regex_match')


@database_sync_to_async
def validate_name_available(value: str):

    if Profile.objects.filter(name=value).exists():

        raise ValidationError(name_availability_validation_error_message, code='name_in_db')


def validate_journal_format(value: str):

    journal_rePattern = "(?!0)\d{3}"

    if not regex.fullmatch(pattern=journal_rePattern, string=value):

        raise ValidationError(journal_format_validation_error_message, code='regex_match')


@database_sync_to_async
def validate_journal_name_available(value: str):

    if Journal.objects.filter(name=value).exists():

        raise ValidationError(journal_name_availability_validation_error_message, code='name_in_db')


@database_sync_to_async
def validate_journal_name_in_base(value: str):

    if not Journal.objects.filter(name=value).exists():

        raise ValidationError(journal_name_in_base_validation_error_message, code='name_in_db')


def validate_ordinal_format(value: str):

    ordinal_rePattern = "(?!0)\d{1,2}"

    if not regex.fullmatch(pattern=ordinal_rePattern, string=value):

        raise ValidationError(ordinal_format_validation_error_message, code='regex_match')


def validate_strength_format(value: str):

    sterngth_rePattern = "(?!0)\d{2}"

    if not regex.fullmatch(pattern=sterngth_rePattern, string=value):

        raise ValidationError(strength_format_validation_error_message, code='regex_match')


@dispatcher.register('profileform')
class ProfileForm(Form):
    journal = fields.TextField(journal_field_message, validators=[validate_journal_format, validate_journal_name_in_base])
    name = fields.TextField(name_field_message, validators=[validate_name_format, validate_name_available]) # TODO: accent on order
    ordinal = fields.TextField(ordinal_field_message, validators=[validate_ordinal_format])

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(ProfileForm)
        user_id = message.from_user.id
        # if not Profile.objects.filter(external_id=user_id).exists():

        try:
            await add_profile(data, user_id)
            await message.answer(text=profile_form_callback_message)
            logging.info(f"A profile created for user_id {user_id}")


        except Exception as e:
            await message.answer(text=on_registration_fail_text)
            logging.error(f"Failed to create a profile for user_id {user_id}\nError:{e}")

        # else:
        #     await message.answer(text="Помилка, профіль за цим telegram-ID існує")



@dispatcher.register('journalform')
class JournalForm(Form):
    name = fields.TextField(journal_field_message, validators=[validate_journal_format, validate_journal_name_available])
    strength = fields.TextField(strength_field_message, validators=[validate_strength_format])

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(JournalForm)
        group_id = message.chat.id
        # if not Profile.objects.filter(external_id=group_id).exists():

        try:
            await add_journal(data, group_id)
            await message.answer(text=journal_form_callback_message)
            logging.info(f"A journal created for group_id {group_id}")

        except Exception as e:
            await message.answer(text=on_registration_fail_text) #Does not work, no message
            logging.error(f"Failed to create a journal for group_id {group_id}\nError:{e}")

        # else:
        #     await message.answer(text="Помилка, журнал за цим telegram-ID існує")


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
            logging.error(f"Failed to set a status for journal_entry for an entry of profile of user id of {user_id}\nError:{e}")