from aiogram.filters.base import Filter
from aiogram import types


class CurrentUserFilter(Filter):
    key = 'from_user'

    def __init__(self, current_user_id):
        self.current_user_id = current_user_id

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == self.current_user_id



