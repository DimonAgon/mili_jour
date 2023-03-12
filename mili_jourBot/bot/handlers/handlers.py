
from aiogram import types
from aiogram.filters import Command
from .dispatcher import dp, router
from ..models import *
import datetime
from ..forms import *

@router.message(Command(commands='start'))
async def start(message: types.Message):  # Self-presintation of the bot

    greeting = "Привіт, я mili_jour (як Military Journal) бот  я можу робити дві справи: \n" \
           "а) Створити журнал для вашого взводу,\n" \
           "б) Допомогати вам слідкувати за відвідуванням занять без зайвих зусиль, " \
           "Користуйтесь)"

    await message.reply(greeting)


@router.message(Command(commands='help'))
async def help(message: types.Message):

    HELPFUL_REPLY = "Будь ласка ЗАРЕЕСТРУЙТЕСЬ, якщо цього не робили. Для цього зайдіть у бот та викличте команду 'register'" \
               "(Усі команди викликаються /{команда})\n" \
                    "Крайньо не рекомендується знаходитись у групі чужого взводу." \
                    "Заборонено " #TODO: what's forbidden?

    #TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


 
@router.message(Command(commands='who_s_present'))
async def who_s_present(message :types.Message):  # Checks who's present
    today = datetime.date.today()
    # deadline = datetime.timedelta(hours=8, minutes=5)
    question = str(today) + " Присутні"
    await message.answer_poll(question=question, options=["Я", "Відсутній"], type='quiz', correct_option_id=0,
                              is_anonymous=False, allows_multiple_answers=False)

    # JournalEntry.objects.create(journal=message.chat.id, date=today, name=message.from_user.id)



@router.message(Command(commands='register'))
async def register(message:types.Message):
    chat_id = message.chat.id

    await message.reply(ProfileForm._meta.labels['name'])

    await dp.wa

    name = message.text

    await message.reply(ProfileForm._meta.labels['ordinal'])

    ordinal = message.text

    initial_data = {'name':name, 'ordinal': ordinal}

    profile = ProfileForm(initial=initial_data)

    #if profile.is_valid():
    #     Profile.objects.create(external_id=message.from_user.username, name=, journal_id=message.chat.id)
    await message.reply("Ви були зареєстровані")

# async def last(message:types.Message):
#
#     entries = JournalEntry.objects.filter(date=date)
#     # entries_list = list(map(lambda x: x.))
#     # attendance_list =
#
#     # await message.reply(entry.)
#
# dp.poll_handler()



# async def on_date(message:types.Message, date):
#
#     await message.reply()



# @dp.poll_answer_handler()
# async def presence_poll_answer_handler(poll_answer:types.PollAnswer):
#     answer_id = poll_answer.option_ids
#     user_id = poll_answer.user.id
#     poll_id = poll_answer.poll_id
#     entry = JournalEntry(date=date.today(), journal_id=types.chat.Chat.id

