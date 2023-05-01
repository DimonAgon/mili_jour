
from aiogram import F
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from aiogram_forms import FormsManager

from .dispatcher import dp, router, bot
from ..models import *
from ..forms import *
from ..views import *
from .filters import *
from ..infrastructure.enums import *

from django.core.validators import validate_comma_separated_integer_list

from channels.db import database_sync_to_async
import asyncio

from enum import Enum

import datetime

import random

import portion as P


@router.message(Command(commands='start'))
async def start_command(message: types.Message):  # Self-presintation of the bot

    greeting = "Mili_jour (Military Journal)." \
               " Бота створено для підтримки роботи командирського складу учбових взводів." \
               " Надано можливість ведення журналу відвідувань через команди. Проект на стадії розробки." \
               " Дійовість деяких аспектів буде перевірена та перероблена за необхідності."

    await message.reply(greeting)


@router.message(Command(commands='help'))
async def help_command(message: types.Message):
    HELPFUL_REPLY = f"Для роботи необхідно виконати реєстрацію журналу взводу та ЗАРЕЕСТРУВАТИСЬ." \
                    "\nПодальше, право на взаємодію із ботом покладається на командирський склад." \
                    "\nСписок команд наведено нижче:" \
                    "\n/start– введення у бот" \
                    "\n/help– інструкція до взаємодії із ботом" \
                    "\n/register– реєструвати профіль" \
                    "\n/register_journal– створити журнал відвідувань" \
                    "\n/cancel_registration– відмінити реєстрацію" \
                    "\n/who_s_present– створити опитування щодо присутності" \
                    "\n/today_report– викликати звіт за сьогоднішній день" \
                    "\n/last_report– викликати останній звіт" \
                    "\n/on_date_report– викликати звіт за датою"

    # TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


class PresencePollOptions(Enum):
    Present = 0
    Absent = 1

def presence_option_to_string(presenceOption: Type[PresencePollOptions]):
    match presenceOption:
        case PresencePollOptions.Present:
            return "Я"
        case PresencePollOptions.Absent:
            return "Відсутній"


@router.message(Command(commands='who_s_present'), F.chat.type.in_({'group', 'supergroup'}))# TODO: add an enum for zoom-mode, add an enum for schedule mode
async def who_s_present_command(message: types.Message, command: CommandObject):  # Checks who is present
    if command.args:
        args = command.args.split()
        mode, *secondary = args
    else: mode = default

    if not mode in [getattr(WhoSPresentMode, attribute) for attribute in vars(WhoSPresentMode)]:
        await message.answer(text="Помилка, вказано невірний режим")
        logging.error(f"Command initiation failed\nError: no such mode \"{mode}\"")
        return

    if mode == WhoSPresentMode.LIGHT_MODE or mode == WhoSPresentMode.NORMAL_MODE or mode == WhoSPresentMode.HARDCORE_MODE:
        try:
            secondary_integers = [int(e) for e in secondary]

        except Exception as e:
            await message.answer(text="Помилка, очікується послідовність занять")
            logging.error(f"Command initiation failed\nError:{e}")
            return

    else:
        try:
            validate_comma_separated_integer_list(secondary)
            await message.answer(text="Помилка, даний режим послідовність занять")
            logging.error("Command initiation failed\nError: no arguments expected")
            return

        except Exception:
            pass


    lessons = secondary_integers
    lessons.sort()

    now = datetime.datetime.now()
    today = now.date()

    group_id = message.chat.id

    if mode == WhoSPresentMode.LIGHT_MODE:
        deadline_time = datetime.time(hour=15, minute=45, second=0)
        deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute, second=deadline_time.second)
        question = str(today) + " Присутність"

    till_deadline = deadline - now

    if not mode == WhoSPresentMode.LIGHT_MODE:
        await initiate_today_report(today, lessons, group_id, mode)
        await initiate_today_entries(today, lessons, group_id, mode)
        for l in lessons:
            lesson_time_interval = Schedule.lessons[l]
            now = datetime.datetime.now()
            start_time = lesson_time_interval.lower
            end_time = lesson_time_interval.upper

            if mode == WhoSPresentMode.HARDCORE_MODE:
                lower = start_time
                upper = end_time
                lower_today = now.replace(hour=lower.hour, minute=lower.minute, second=lower.second)
                upper_today = now.replace(hour=upper.hour, minute=upper.minute, second=lower.second)
                lower_today_timestamp = lower_today.timestamp()
                upper_today_timestamp = upper_today.timestamp()
                lower_today_timestamp_integer = int(lower_today_timestamp)
                upper_today_timestamp_integer = int(upper_today_timestamp)
                random_datetime_timestamp_integer = random.randint(lower_today_timestamp_integer,
                                                                   upper_today_timestamp_integer)
                random_datetime = datetime.datetime.fromtimestamp(random_datetime_timestamp_integer)

                poll_time = random_datetime

            else:
                poll_time = start_time

            deadline = end_time
            till_start = now.replace(hour=poll_time.hour, minute=poll_time.minute, second=poll_time.second)
            poll_message = await message.answer_poll()

    else:
        await initiate_today_entries(today, group_id)# TODO: the better choice may be to call function on every study day
        #await initiate_today_report(today, group_id, lessons)
        poll_message = await message.answer_poll(question=question, options=list(presence_option_to_string(o) for o in PresencePollOptions), type='quiz', correct_option_id=0, is_anonymous=False, allows_multiple_answers=False, protect_content=True)
        await asyncio.sleep(till_deadline.seconds)# TODO: schedule instead
        await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)

    today_report = await report(today, group_id, lessons, mode)
    await message.answer(today_report)
    #report(today, group_id, lessons, mode)


    mode = default


class Schedule: #Do not try to deceive the poll
    first_lesson = P.openclosed(datetime.time(8, 10, 0), datetime.time(10, 0, 0))
    second_lesson = P.openclosed(datetime.time(10, 20, 0), datetime.time(11, 55, 0))
    third_lesson = P.openclosed(datetime.time(12, 15, 0), datetime.time(13, 50, 0))
    fourth_lesson = P.openclosed(datetime.time(14, 10, 0), datetime.time(15, 45, 0))
    fifth_lesson = P.openclosed(datetime.time(16, 5, 0), datetime.time(17, 30, 0))

    lessons = {1: first_lesson, 2: second_lesson, 3: third_lesson, 4: fourth_lesson, 5: fifth_lesson}

    @classmethod
    def lesson_match(cls, time):
        lessons = cls.lessons

        for l in lessons:
            if lessons[l].contains(time):

                return l
        return None



class AbsenceReasonStates(StatesGroup): AbsenceReason = State()

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Т'))
async def absence_reason_handler_T(message: types.Message, forms: FormsManager):
    await forms.show('absenceform')

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Н'))
async def absence_reason_handler_H(message: types.Message, state: FSMContext):
    await state.clear()

@router.poll_answer()# TODO: add a flag for vote-answer mode, add an every-lesson mode
async def who_s_present_poll_handler (poll_answer: types.poll_answer, state: FSMContext):  #TODO: add an ability to re-answer
    now = datetime.datetime.now()# TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    is_present = poll_answer.option_ids == [PresencePollOptions.Present.value]

    if is_present:
        lesson = Schedule.lesson_match(now_time)
    else: lesson = None

    if not is_present or lesson:
        user_id = poll_answer.user.id

    if lesson:
        await on_lesson_view(lesson, user_id, now_date)

    if not is_present:
        await if_absent_view(user_id, now_date)
        await bot.send_message(user_id, 'Вказати причину відстутності? Т/Н')
        await state.set_state(AbsenceReasonStates.AbsenceReason)


@router.message(Command(commands='register'), F.chat.type.in_({'private'}))#, RegisteredExternalIdFilter(Profile)
async def register_command(message: types.Message, forms: FormsManager):

    await message.reply(text='ініціюю реєстрацію')
    await asyncio.sleep(3)

    await forms.show('profileform')



@router.message(Command(commands='register_journal'), F.chat.type.in_({'group', 'supergroup'}))
async def register_journal_command(message: types.Message, forms: FormsManager):

    await message.reply(text="Ініціюю реєстрацію взводу")
    await asyncio.sleep(3)

    await forms.show('journalform')


@router.message(Command(commands='cancel_registration'))
async def cancel_registration_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply(text="Процес реєстрації було перервано")
# TODO: reports should be able in both group and private chat
    # TODO: when printing a report: use sort by a lesson and then by ordinal


@router.message(Command(commands='today_report'))
async def today_report_command(message: types.Message):
    today = datetime.datetime.today().date()
    group_id = message.chat.id

    report = get_report(today, group_id)
    message.answer(report.table)
    #message.answer(report.summary)


@router.message(Command(commands='last_report'))
async def last_report_command(message: types.Message):# TODO: use report model to answer

    pass


@router.message(Command(commands='on_date_report'))
async def on_date_report_command(message: types.Message):
    #date =
    pass

    #message.answer(report(date, message))



# TODO: create a chat leave command, should delete any info of-group info
# TODO: create a new_schedule_command

