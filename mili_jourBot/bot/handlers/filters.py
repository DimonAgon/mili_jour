from aiogram.filters.base import Filter
from aiogram import types
from typing import Type
from django.db import models


class RegisteredExternalIdFilter(Filter):
    key = "in_db"

    async def __call__(self, model: Type[models.Model], message: types.Message, chat_mode: bool = False) -> bool:

        if chat_mode:
            id_ = message.chat.id
        else:
            id_ = message.from_user.id
        return model.objects.filter(external_id=id_).exists()

