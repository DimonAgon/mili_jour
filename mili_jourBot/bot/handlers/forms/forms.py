
from ..logger import handlers_logger as logger

from aiogram import types

from aiogram_forms import Form, fields, FormsManager
from aiogram_forms.errors import ValidationError
from aiogram.filters.state import State, StatesGroup

from channels.db import database_sync_to_async

from .dispatcher import dispatcher
from .fields import NamedTextField
from ..dispatcher import bot
from ...db_actions import *
from ...models import *
from static_text.chat_messages import *
from static_text.logging_messages import *
from misc.re_patterns import *
from misc.exceptions import *

from django.core.exceptions import ValidationError as DjangoCoreValidationError

from key_generator.key_generator import generate


# TODO: add an ordinal filter
# TODO forms: add logging errors for all the validations
# TODO: add 'Form' to part to forms classes to prevent models shadowing


def validate_name_format(value: str):
    if not regex.fullmatch(pattern=full_name_rePattern, string=value):
        logger.error(profile_name_format_validation_fail_logging_error_message)
        raise ValidationError(profile_name_format_validation_fail_chat_error_message, code='regex_match')

    logger.info(profile_name_format_validation_success_logging_info_message)


@database_sync_to_async
def validate_name_available(value: str):
    profile_attributes = {'name': value}
    if Profile.objects.filter(**profile_attributes).exists():
        logger.error(
            profile_is_not_registered_by_attributes_check_fail_logging_error_message.format(
                profile_attributes=profile_attributes
            )
        )
        raise ValidationError(
            profile_is_not_registered_by_attributes_check_fail_logging_error_message.format(
                profile_attributes=attributes_kw
            ),
            code='name_in_db'
        )

    logger.info(
        profile_is_not_registered_by_attributes_check_success_logging_info_message.format(
            profile_attributes=profile_attributes
        )
    )


def validate_journal_format(value: str):
    if not regex.fullmatch(pattern=journal_rePattern, string=value):
        logger.error(journal_name_format_validation_fail_chat_error_message)
        raise ValidationError(journal_name_format_validation_fail_chat_error_message, code='regex_match')

    logger.info(journal_name_format_validation_success_logging_info_message)


@database_sync_to_async
def validate_journal_name_available(value: str):
    journal_attributes = {'name': value}
    if Journal.objects.filter(**journal_attributes).exists():
        logger.error(
            journal_is_not_registered_by_attributes_check_fail_logging_error_message.format(
                journal_attributes=journal_attributes
            )
        )
        raise ValidationError(
            journal_is_not_registered_by_attributes_check_fail_chat_error_message.format(
                journal_attributes=attributes_kw
            ),
            code='name_in_db'
        )

    logger.info(
        journal_is_not_registered_by_attributes_check_success_logging_info_message.format(
            journal_attributes=journal_attributes
        )
    )


@database_sync_to_async
def check_journal_is_registered_by_name(name: str):
    journal_attributes = {'name': name}
    if not Journal.objects.filter(**journal_attributes).exists():
        logger.error(
            journal_is_registered_by_attributes_check_fail_logging_error_message.format(
                journal_attributes=journal_attributes
            )
        )
        raise ValidationError(
            journal_is_registered_by_attributes_check_fail_chat_error_message.format(
                journal_attributes=attributes_kw
            ),
            code='name_in_db'
        )

    logger.info(
        journal_is_registered_by_attributes_check_success_logging_info_message.format(
            journal_attributes=journal_attributes
        )
    )


def validate_ordinal_format(value: str):
    if not regex.fullmatch(pattern=ordinal_rePattern, string=value):
        logger.error(profile_ordinal_format_validation_fail_logging_error_message)
        raise ValidationError(profile_ordinal_format_validation_fail_chat_error_message, code='regex_match')


def validate_strength_format(value: str):
    if not regex.fullmatch(pattern=sterngth_rePattern, string=value):
        logger.error(journal_strength_format_validation_fail_logging_error_message)
        raise ValidationError(journal_strength_format_validation_fail_chat_error_message, code='regex_match')

    logger.info(journal_strength_format_validation_success_logging_info_message)


def validate_super_user_key(value: str, authentic_key, user_id):
    if not value == authentic_key:
        raise DjangoCoreValidationError(key_validation_fail_logging_error_message, code='superuser_key')

    logger.info(key_validation_success_logging_info_message)


class IsEnteredValidator:
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __call__(self, value):
        if value:
            logger.info(was_entered_pp.format(something=f"{self.field_name} '{value}'"))

        else:
            raise DjangoCoreValidationError(f"{has_not_been_entered_pp.format(something=self.field_name)}",
                                            code='name')


journal_name_is_entered_validator = IsEnteredValidator("journal name")
journal_strength_is_entered_validator = IsEnteredValidator("journal strength")
profile_name_is_entered_validator = IsEnteredValidator("profile name")
profile_ordinal_is_entered_validator = IsEnteredValidator("profile ordinal")
absence_reason_is_entered_validator = IsEnteredValidator(absence_reason_kwс)


@dispatcher.register('profileform')
class ProfileForm(Form):
    journal_name = NamedTextField(
        name=journal_kw,
        label=journal_name_chat_field_message,
        validators=[
            journal_name_is_entered_validator,
            validate_journal_format,
            check_journal_is_registered_by_name,
        ]
    )
    name = NamedTextField(
        name=profile_kw,
        label=profile_name_chat_field_message,
        validators=[
            profile_name_is_entered_validator,
            validate_name_format,
        ]
    )  # TODO: accent on order
    ordinal = NamedTextField(
        name=profile_ordinal_kw,
        label=profile_ordinal_chat_field_message,
        validators=[
            profile_ordinal_is_entered_validator,
            validate_ordinal_format,
        ]
    )

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(ProfileForm)
        user_id = message.from_user.id
        journal_data = {'name': data['journal']}
        journal = await get_journal_async(journal_data)
        journal_group_id = journal.external_id

        try:
            status = await bot.get_chat_member(journal_group_id, user_id)
            if status.status == 'left':
                raise UserNotInGroupException  # TODO: add logging

            else:
                profile_attributes = {'external_id': user_id, 'journal': journal}; profile_attributes.update(data)
                await add_profile(profile_attributes)

        except Exception as e:
            await message.answer(text=registration_fail_chat_error_message)
            logger.error(
                registration_fail_logging_error_message.format(
                    model="Profile",
                    model_attributes=profile_attributes
                ),
                exc_info=True
            )

        await message.answer(text=profile_registration_success_chat_info_message)
        logger.info(
            profile_registration_success_chat_info_message.format(
                profile_attributes=profile_attributes
            )
        )


@dispatcher.register('journalform')
class JournalForm(Form):
    name = NamedTextField(
        name=journal_name_kw,
        label=journal_name_chat_field_message,
        validators=[
            journal_name_is_entered_validator,
            validate_journal_format,
        ]
    )
    strength = NamedTextField(
        name=journal_strength_kw,
        label=journal_strength_chat_field_message,
        validators=[
            journal_strength_is_entered_validator,
            validate_strength_format,
        ]
    )

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(JournalForm)
        group_id = message.chat.id


        try:
            journal_attributes = {'external_id': group_id}; journal_attributes.update(data)
            await add_journal(journal_attributes)

        except Exception:
            await message.answer(text=registration_fail_chat_error_message)  # Does not work, no message
            logger.error(
                registration_fail_logging_error_message.format(
                    model="Journal",
                    model_attributes=journal_attributes
                ),
                exc_info=True
            )

            return

        await message.answer(text=journal_registration_success_chat_info_message)
        logger.info(
            journal_registration_success_logging_info_message.format(
                journal_attributes=journal_attributes
            )
        )


@dispatcher.register('absenceform')
class AbsenceReason(Form):
    status = NamedTextField(
        name=status_kw,
        label=absence_reason_status_chat_field_message, #TODO: move field help-text to 'help' attribute
        validators=[absence_reason_is_entered_validator]
    )

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(AbsenceReason)
        user_id = message.from_user.id

        try:
            await set_status(data, user_id)

        except Exception:
            await message.answer(text=absence_reason_share_fail_chat_error_message)
            logger.error(
                absence_reason_share_fail_logging_error_message.format(
                    absence_reason_attributes=f"'{message.text}'"
                ),
                exc_info=True
            )
            return

        logger.info(
            absence_reason_share_success_logging_info_message.format(
                absence_reason_attributes=f"'{message.text}'"
            )
        )
        await message.answer(absence_reason_share_success_chat_info_message)


# TODO: consider adding states-file
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