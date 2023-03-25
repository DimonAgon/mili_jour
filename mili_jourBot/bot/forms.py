from django import forms
from .models import Profile
from django.core import exceptions
from aiogram.filters.state import State, StatesGroup
from aiogram_forms import Form, fields, dispatcher
import regex



@dispatcher.register('profileform')
class ProfileForm(Form):
    name = fields.TextField(label="Ваше Прізвище та Ім'я", validators=['checkname'])
    journal = fields.TextField(label="Номер вашого взводу")
    ordinal = fields.TextField(label="Ваш номер у списку")


def check_name(name):

    name_rePattern = "\p{L}*\s\p{Lu}{1}\p{L}+(?:[- ])?\p{Lu}{1}\p{L}+"

    if regex.match(pattern=name_rePattern, string=name):

        raise exceptions.ValidationError("Введіть ім'я коректно")

    return name


def check_journal(journal):

    journal_rePattern = "(?!0)\d{3}"

    if regex.match(pattern=journal_rePattern, string=journal):

        raise exceptions.ValidationError("Введіть номер взводу коректно")

    return journal


def check_ordinal(ordinal):

    ordinal_rePattern = "(?!0)\d{1,2}"

    if regex.match(pattern=ordinal_rePattern, string=ordinal):

        raise exceptions.ValidationError("Введіть номер коректно")

    return ordinal
