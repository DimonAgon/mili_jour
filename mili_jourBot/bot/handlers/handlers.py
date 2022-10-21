from aiogram import types
from .dispatcher import dp
from ..models import *
from datetime import date
from ..forms import *


@dp.message_handler(
    commands=['start', 'last', 'on_date', 'presence_reco']
)

async def start(message: types.Message):
    mess = "Привіт, я mili_jour бот (як Military Journal) я можу робити дві речі: " \
           "а) Створити журнал для вашого взводу," \
           "б) Допомогати вам слідкувати за відвідуванням занять без зайвих зусиль, " \
           "Користуйтесь)"

    await message.reply(mess)

async def presence_reco(message:types.Message):
    today = date.today()
    await message.answer_poll(question=today, options=["Так", "Ні"], type='quiz', correct_option_id=1, is_anonymous=False)

async def on_date(message:types.Message, requested_date):
    await message.reply()

async def register(message:types.Message):
    await message.reply(ProfileForm._meta.labels['name'])
    # wait for input + write into var
    # validate name
    # todo:
    # insert name into user by user id
    #
    profile = ProfileForm()
    if profile.is_valid():
        Profile.objects.create(external_id=message.from_user.username, name=name, journal_id=message.chat.id)
    await message.reply("Ви були зареєстровані")


async def last(message:types.Message):
    JournalEntry.objects.earliest('date')



