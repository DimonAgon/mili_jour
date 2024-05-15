
from aiogram_forms.forms.base import Field
from aiogram_forms import fields

from typing import List, Union, Optional, Mapping, Callable, Awaitable


class NamedField:
    def __init__(self, name):
        self.name = name

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case 'name':
                return self.name


class NamedTextField(NamedField, fields.TextField):
    def __init__(
            self,
            name,
            label: 'TranslatableString',
            help_text: Optional['TranslatableString'] = None,
            error_messages: Optional[Mapping[str, 'TranslatableString']] = None,
            validators: Optional[List[Union[Callable[..., None], Callable[..., Awaitable[None]]]]] = None

    ) -> None:
        NamedField.__init__(self, name)
        fields.TextField.__init__(self, label, help_text, error_messages, validators)
