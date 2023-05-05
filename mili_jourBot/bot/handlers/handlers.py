import re

from aiogram import F
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from aiogram_forms import FormsManager
from aiogram_forms.errors import ValidationError

from .dispatcher import dp, router, bot
from ..models import *
from ..forms import *
from ..views import *
from .filters import *
from ..infrastructure.enums import *
from ..infrastructure import enums

from django.core.validators import validate_comma_separated_integer_list

from channels.db import database_sync_to_async
import asyncio

import datetime

import random



def validate_date_format(value):
    date_format = '%d-%m-%Y'

    try:
        datetime.datetime.strptime(value, date_format)
        return value

    except:
        raise ValidationError("Ввести дату коректно", code='format_match')



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

def presence_option_to_string(presence_option: Type[PresencePollOptions]):
    match presence_option:
        case PresencePollOptions.Present:
            return "Я"
        case PresencePollOptions.Absent:
            return "Відсутній"


@router.message(Command(commands=['who_s_present', 'wp']), F.chat.type.in_({'group', 'supergroup'}))
async def who_s_present_command(message: types.Message, command: CommandObject):  # Checks who is present
    aftercommand = command.args
    if aftercommand:
        args = aftercommand.split()
        pseudo_mode, *secondary = args
    else:
        await message.answer("Помилка, вкажіть аргументи")
        logging.error("Command initiation failed\nError: no arguments")
        return

    mode = next((mode for mode in WhoSPresentMode if mode.value == pseudo_mode), None)

    if not mode:
        await message.answer("Помилка, вказано невірний режим")
        logging.error(f"Command initiation failed\nError: no such mode \"{pseudo_mode}\"")
        return

    if mode == WhoSPresentMode.LIGHT_MODE or mode == WhoSPresentMode.NORMAL_MODE or mode == WhoSPresentMode.HARDCORE_MODE:
        try:
            secondary[0]
            secondary_integers = [int(e) for e in secondary]

        except Exception as e:
            await message.answer("Помилка, очікується послідовність занять")
            logging.error(f"Command initiation failed\nError:{e}")
            return

        if [i for i in secondary_integers if i in Schedule.lessons_intervals.keys()] == [i for i in secondary_integers]:
            lessons = secondary_integers

        else:
            await message.answer("Помилка, невірно вказані заняття")
            logging.error("Command initiation failed\nError: wrong arguments")
            return

    else:
        try:
            validate_comma_separated_integer_list(secondary)
            await message.answer("Помилка, режим не потребує послідовності занять")
            logging.error("Command initiation failed\nError: no arguments expected")
            return

        except Exception:
            pass # TODO: consider pass

    lessons.sort()

    now = datetime.datetime.now()
    today = now.date()
    now_time = now.time()
    string_today = str(today)

    group_id = message.chat.id

    poll_configuration = {'options': list(presence_option_to_string(o) for o in PresencePollOptions),
                           'type': 'quiz', 'correct_option_id': 0,
                           'is_anonymous': False,
                           'allows_multiple_answers': False,
                           'protect_content': True}

    if mode == WhoSPresentMode.LIGHT_MODE:
        last_lesson = lessons[-1]
        last_lesson_time = Schedule.lessons_intervals[last_lesson]
        deadline_time = last_lesson_time.upper
        deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute, second=deadline_time.second)
        till_deadline = deadline - now
        question = string_today + " Присутність"
        poll_configuration.update({'question': question})

    if not mode == WhoSPresentMode.LIGHT_MODE:
        await initiate_today_report(today, group_id, lessons)
        for lesson in lessons:

            await initiate_today_entries(today, group_id, lesson, mode)

            question = string_today + f" Заняття {str(lesson)}"
            poll_configuration.update({'question': question})

            lesson_time_interval = Schedule.lessons_intervals[lesson]
            if lesson_time_interval.contains(now_time): start_time = start_time = (now + datetime.timedelta(seconds=1)).time()
            elif now_time < lesson_time_interval.lower:  start_time = lesson_time_interval.lower
            else:
                logging.info(f"lesson {lesson} iteration skipped, lesson time is over")
                continue

            end_time = lesson_time_interval.upper
            deadline = now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)


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
                random_lesson_datetime = datetime.datetime.fromtimestamp(random_datetime_timestamp_integer)

                poll_time = now.replace(hour=random_lesson_datetime.hour, minute=random_lesson_datetime.minute, second=random_lesson_datetime.second)

            else: poll_time = now.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)

            till_poll = poll_time - now
            await asyncio.sleep(till_poll.seconds)
            till_deadline = deadline - now # TODO: create an async scheduler
            poll_message = await message.answer_poll(**poll_configuration) #TODO: consider using poll configuration dict
            await asyncio.sleep(till_deadline.seconds)  # TODO: schedule instead
            await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)


    else:
        await initiate_today_entries(today, group_id)# TODO: the better choice may be to call function on every study day
        await initiate_today_report(today, group_id, lessons)
        poll_message = await message.answer_poll(**poll_configuration)
        await asyncio.sleep(till_deadline.seconds)# TODO: schedule instead
        await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)

    today_report = await report_today(today, group_id, lessons, mode)
    await message.answer(today_report.table)
    await message.answer(today_report.summary, disable_notification=True)


class AbsenceReasonStates(StatesGroup): AbsenceReason = State()

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Т'))
async def absence_reason_handler_T(message: types.Message, forms: FormsManager):
    await forms.show('absenceform')

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Н'))
async def absence_reason_handler_H(message: types.Message, state: FSMContext):
    await state.clear()

@router.poll_answer()# TODO: add a flag for vote-answer mode, add an every-lesson mode
async def who_s_present_poll_handler (poll_answer: types.poll_answer, state: FSMContext):  #TODO: add an ability to re-answer
    is_present = poll_answer.option_ids == [PresencePollOptions.Present.value]
    user_id = poll_answer.user.id

    await presence_view(is_present, user_id)

    if not is_present:
        today_status = await get_today_status(user_id)
        if today_status:
            await set_status({'status': today_status}, user_id)

        else:
            await bot.send_message(user_id, 'Вказати причину відстутності? Т/Н')
            await state.set_state(AbsenceReasonStates.AbsenceReason)

@router.message(Command(commands='absence_reason'))
async def absence_reason_command(message: types.Message, state: FSMContext):
    user_id = message.user.id

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


@router.message(Command(commands='today_report'))
async def today_report_command(message: types.Message):
    group_id = message.chat.id

    today_report = await get_report(group_id, GetReportMode.TODAY)

    message.answer(today_report.table)
    message.answer(today_report.summary, disable_notification=True)


@router.message(Command(commands='last_report'))
async def last_report_command(message: types.Message):# TODO: use report model to answer
    group_id = message.chat.id
    last_report = await get_report(group_id, GetReportMode.LAST)

    message.answer(last_report.table)
    message.answer(last_report.summary, disable_notification=True)


@router.message(Command(commands='on_date_report'))
async def on_date_report_command(message: types.Message, command: CommandObject):
    aftercommand = command.args
    if validate_date_format(aftercommand):
        date = aftercommand

    group_id = message.chat.id

    on_date_report = await get_report(group_id, GetReportMode.ON_DATE, date)

    message.answer(on_date_report.table)
    message.answer(on_date_report.summary, disable_notification=True)


# TODO: create a chat leave command, should delete any info of-group info
# TODO: create a new_schedule_command

