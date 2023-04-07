from aiogram.filters.base import Filter
from aiogram import types
from aiogram.fsm.context import FSMContext

class CurrentUserFilter(Filter):
    key = 'from_user'

    def __init__(self):

        self.state = FSMContext
        self.current_user_id = self.state.get_data('current_user_id')

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id == self.current_user_id



