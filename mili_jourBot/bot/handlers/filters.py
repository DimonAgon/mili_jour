from aiogram.filters import BaseFilter
from aiogram import types

from typing import Type

from django.db import models

from channels.db import database_sync_to_async


class RegisteredExternalIdFilter(BaseFilter):
    key = "in_db"
    def __init__(self, model: Type[models.Model], chat_mode: bool = False):
        self.model = model
        self.chat_mode = chat_mode

    @database_sync_to_async
    def __call__(self, message: types.Message) -> bool:

        if self.chat_mode:
            id_ = message.chat.id
        else:
            id_ = message.from_user.id
        return not self.model.objects.filter(external_id=id_).exists()

