# TODO: add a security measurement: for only authorized journals allow commands

from aiogram import F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .dispatcher import dp, router, bot
from ..models import *
from ..forms import *
from ..views import *

import datetime
import portion as P

import asyncio



@router.message(Command(commands='start'))
async def start_command(message: types.Message):  # Self-presintation of the bot

    greeting = "Привіт, я mili_jour (як Military Journal) бот  я можу робити дві справи: \n" \
               "а) Створити журнал для вашого взводу,\n" \
               "б) Допомогати вам слідкувати за відвідуванням занять без зайвих зусиль, " \
               "Користуйтесь)"

    await message.reply(greeting)


@router.message(Command(commands='help'))
async def help_command(message: types.Message):
    HELPFUL_REPLY = "Будь ласка ЗАРЕЕСТРУЙТЕСЬ, якщо цього не робили. Для цього зайдіть у бот та викличте команду 'register'" \
                    "(Усі команди викликаються /{команда})\n" \
                    "Крайньо не рекомендується знаходитись у групі чужого взводу.\n" \
                    "Заборонено запрошувати бот не у групи-взводи"

    # TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


@router.message(Command(commands='who_s_present'))  # TODO: add a flag for zoom-mode
async def who_s_present_command(message: types.Message):  # Checks who's present
    now = datetime.datetime.now()
    today = now.date()
    deadline_time = datetime.time(hour=17, minute=5)
    deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute)
    till_deadline = deadline - now
    question = str(today) + " Присутні"

    poll_message = await message.answer_poll(question=question, options=["Я", "Відсутній"], type='quiz', correct_option_id=0, is_anonymous=False, allows_multiple_answers=False, protect_content=True)

    await asyncio.sleep(300)  # till_deadline.total_seconds())
    await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)


class Schedule: #Do not try to decieve the poll
    first_lesson = P.openclosed(datetime.time(8, 25, 0), datetime.time(10, 0, 0))
    second_lesson = P.openclosed(datetime.time(10, 20, 0), datetime.time(11, 55, 0))
    third_lesson = P.openclosed(datetime.time(12, 15, 0), datetime.time(13, 50, 0))
    fourth_lesson = P.openclosed(datetime.time(14, 10, 0), datetime.time(15, 45, 0))
    fifth_lesson = P.openclosed(datetime.time(16, 5, 0), datetime.time(17, 30, 0))

    lessons = {1: first_lesson, 2: second_lesson, 3: third_lesson, 4: fourth_lesson, 5: fifth_lesson}


@router.poll_answer(F.option_ids.contains(0))  # TODO: add a flag for vote-answer mode
def handle_who_s_present(poll_answer: types.poll_answer):  # TODO: add an every-lesson mode
    now = datetime.datetime.now()# TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    lessons = Schedule.lessons
    for l in lessons:
        if lessons[l].contains(now_time):
            lesson = l

    if lesson:
        user_id = poll_answer.user.id
        profile = Profile.objects.get(external_id=user_id)
        journal = Journal.objects.get(name=profile.journal)
        initial = {'journal': journal, 'profile': profile,  'date': now_date, 'lesson': lesson, 'status': True}
        #add_journal_entry(initial)


@router.message(Command(commands='register'))
async def register_command(message: types.Message, forms: FormsManager):
    await message.reply(text='ініціюю реєстрацію')
    await asyncio.sleep(3)
    await forms.show('profileform')

# TODO: reports should be able in both group and private chat
    # TODO: when printing a report: use sort by a lesson and then by ordinal



# async def last(message: types.Message):
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
#   answer_id = poll_answer.option_ids
#   user_id = poll_answer.user.id
#   poll_id = poll_answer.poll_id


# TODO: craete a chat leave command
