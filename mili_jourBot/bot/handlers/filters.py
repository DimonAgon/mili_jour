from aiogram.filters import BaseFilter
from aiogram import types

from typing import Type

from django.db import models

from channels.db import database_sync_to_async

from .dispatcher import bot


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

class IsAdminFilter(BaseFilter):
    key = 'is_admin'
    required_auth_level = 'administrator'
    creator = 'creator'

    async def __call__(self, message: types.Message):
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        member = await bot.get_chat_member(chat_id, user_id)
        is_admin = member.status == self.required_auth_level or member.status == self.creator

        return is_admin
