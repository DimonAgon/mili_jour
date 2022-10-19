from aiogram import types
from .dispatcher import dp
from ..models import *


@dp.message_handler(
    commands=['start', 'last', 'on_date']
)

async def start(message: types.Message):
    mess = "Привіт, я mili_jour бот (як Military Journal) я можу робити дві речі: " \
           "а) Створити журнал для вашого взводу," \
           "б) Допомогати вам слідкувати за відвідуванням занять без зайвих зусиль, " \
           "Користуйтесь)"

    await message.reply(mess)


@dp.poll_handler(
    commands=['new_journal']
)
async def new_journal(squadron, external_id):
    Journal(name=squadron, external_id=external_id)

#
# @dp.answer_handler(comands=['presence_reco'])
# async def presence_reco():
#     pass
#
