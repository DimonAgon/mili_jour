
import pause
from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .dispatcher import dp, router, bot
from ..models import *
from ..forms import *
from ..views import *
import datetime
import asyncio

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
                    "Крайньо не рекомендується знаходитись у групі чужого взводу.\n" \
                    "Заборонено запрошувати бот не у групи-взводи"

    #TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


 
@router.message(Command(commands='who_s_present'))
async def who_s_present(message: types.Message):  # Checks who's present
    now = datetime.datetime.now()
    today = now.date()
    deadline = now + datetime.timedelta(hours=8, minutes=5)
    deadline_timestamp = int(deadline.timestamp())

    question = str(today) + " Присутні"

    poll_message = await message.answer_poll(question=question, options=["Я", "Відсутній"], type='quiz', correct_option_id=0,
                              is_anonymous=False, allows_multiple_answers=False, protect_content=True)

    await pause.until(deadline_timestamp) #TODO: stop on time, not sleep till
    await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)
    # JournalEntry.objects.create(journal=message.chat.id, date=today, name=message.from_user.id)



@router.message(Command(commands='register'))
async def register(message: types.Message, forms: FormsManager):

    await message.reply(text='ініціюю реєстрацію')
    await asyncio.sleep(3)
    await forms.show('profileform')



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


#TODO: craete a chat leave command