
from aiogram_forms import Form, fields, dispatcher, FormsManager
from aiogram_forms.errors import ValidationError
from aiogram import types
import regex
from .views import *


def validate_name_format(value: str):

    name_rePattern = "\p{Lu}\p{Ll}+\s\p{Lu}\p{Ll}+(?:[-]\p{Lu}\p{Ll}+)?" #for any language

    if not regex.fullmatch(pattern=name_rePattern, string=value):

        raise ValidationError("Введіть ім'я коректно", code="regex_match")



def validate_journal_format(value: str):

    journal_rePattern = "(?!0)\d{3}"

    if not regex.fullmatch(pattern=journal_rePattern, string=value):

        raise ValidationError("Введіть номер взводу коректно", code="regex_match")



def validate_ordinal_format(value: str):

    ordinal_rePattern = "(?!0)\d{1,2}"

    if not regex.fullmatch(pattern=ordinal_rePattern, string=value):

        raise ValidationError("Введіть номер коректно", code="regex_match")



@dispatcher.register('profileform')
class ProfileForm(Form):
    name = fields.TextField("Ваше Прізвище та Ім'я", validators=[validate_name_format])
    journal = fields.TextField("Номер вашого взводу", validators=[validate_journal_format])
    ordinal = fields.TextField("Ваш номер у списку", validators=[validate_ordinal_format])

    @classmethod
    async def callback(cls, message: types.Message, forms: FormsManager, **data) -> None:

        data = await forms.get_data(ProfileForm)
        user_id = message.from_user.id

        await add_profile(data, user_id)

        await message.answer(text="Ви були успішно зареєстровані")


