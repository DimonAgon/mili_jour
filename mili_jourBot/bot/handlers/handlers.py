from aiogram import types
from .dispatcher import dp
from ..models import *
from datetime import date

@dp.message_handler(
    commands=['start', 'last', 'on_date', 'new_journal', 'presence_reco']
)

async def start(message: types.Message):
    mess = "Привіт, я mili_jour бот (як Military Journal) я можу робити дві речі: " \
           "а) Створити журнал для вашого взводу," \
           "б) Допомогати вам слідкувати за відвідуванням занять без зайвих зусиль, " \
           "Користуйтесь)"

    await message.reply(mess)

async def new_journal(message: types.Message, squadron):
    pass

async def presence_reco(message:types.Message):
    today = date.today()
    await message.answer_poll(question=today, options=["Так", "Ні"], type='quiz', correct_option_id=1, is_anonymous=False)
    JournalEntry(journal=)

async def on_date(message:types.Message, requested_date):
    await message.reply()


