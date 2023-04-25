
from aiogram import F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from aiogram_forms import FormsManager

from .dispatcher import dp, router, bot
from ..models import *
from ..forms import *
from ..views import *
from .filters import *

import datetime
import portion as P

import  prettytable

import asyncio
from channels.db import database_sync_to_async

from enum import Enum

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


@database_sync_to_async
# TODO: all views to views.py
def initiate_today_entries(today, message: types.Message):# TODO: the better choice may be to call function on every study day
    if not JournalEntry.objects.filter(date=today).exists():
        group_id = message.chat.id
        journal = Journal.objects.get(external_id=group_id)
        profiles = Profile.objects.filter(journal=journal)# TODO: use state-machine for better-performance
        ordered_profiles = profiles.order_by('ordinal')

        for p in ordered_profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'is_present': False})

class PresenceOptions(Enum):
    Present = 0
    Absent = 1

def presence_option_to_string(presenceOption: Type[PresenceOptions]):
    match presenceOption:
        case PresenceOptions.Present:
            return "Я"
        case PresenceOptions.Absent:
            return "Відсутній"

@router.message(Command(commands='who_s_present'), F.chat.type.in_({'group', 'supergroup'}))# TODO: add an enum for zoom-mode, add an enum for schedule mode
async def who_s_present_command(message: types.Message, state: FSMContext):  # Checks who is present
    now = datetime.datetime.now()
    today = now.date()
    deadline_time = datetime.time(hour=17, minute=5)
    deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute)
    seconds_till_deadline = (deadline - now).seconds
    question = str(today) + " Присутність"
    group_id = message.chat.id

    await initiate_today_entries(today, message)
    poll_message = await message.answer_poll(question=question, options=list(presence_option_to_string(o) for o in PresenceOptions), type='quiz', correct_option_id=0, is_anonymous=False, allows_multiple_answers=False, protect_content=True)

    await asyncio.sleep(seconds_till_deadline)# TODO: schedule instead
    await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)


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
class AbsenceReasonStates(StatesGroup):
    status = State()
    entry = State()

@router.message(AbsenceReasonStates.status, F.text.regexp(r'Т'))
def absence_reason_handler(forms: FormsManager, state: FSMContext):
    forms.show('absenceform')

@router.message(AbsenceReasonStates.status, F.text.regexp(r'Н'))
def absence_reason_handler(state: FSMContext):
    await state.clear()

@router.poll_answer()# TODO: add a flag for vote-answer mode, add an every-lesson mode
def who_s_present_handler (poll_answer: types.poll_answer, state: FSMContext):  #TODO: add an ability to re-answer
    now = datetime.datetime.now()# TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    is_present = poll_answer.option_ids == [PresenceOptions.Present.value]

    if is_present:
        lesson = Schedule.lesson_match(now_time)
    else: lesson = None

    if not is_present or lesson:
        user_id = poll_answer.user.id
        profile = Profile.objects.get(external_id=user_id)
        journal = Journal.objects.get(name=profile.journal)
        corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=now_date)
        corresponding_entry.lesson = lesson

    if lesson:
        # TODO: adapt django functions to async
        corresponding_entry.is_present = True

    if not is_present:
        corresponding_entry.is_present = False

        bot.send_message(user_id, 'Вказати причину відстутності? Т/Н')
        state.update_data(entry=corresponding_entry)# TODO: fix async
        state.set_state(AbsenceReasonStates.status)

    corresponding_entry.save()


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


@database_sync_to_async
def report(date, message: types.Message):
    table = prettytable.PrettyTable(["Студент", "З заняття №", "Присутність"])
    group_id = message.chat.id
    journal = Journal.objects.get(external_id=group_id)
    if date == 'last': entries = JournalEntry.objects.filter(journal=journal).latest()
    else: entries = JournalEntry.objects.filter(journal=journal, date=date)

    for entry in entries:
        profile = entry.profile

        if entry.is_present: presence = "·"
        else: presence = "н/б"

        table.add_row([str(profile), entry.lesson, presence])
    return str(table)

@router.message(Command(commands='today_report'))
async def today_report_command(message: types.Message):
    today = datetime.datetime.today().date()
    today_report = await report(today, message)
    await message.answer(today_report)


@router.message(Command(commands='last_report'))
async def last_report_command(message: types.Message):# TODO: use report model to answer
    date = 'last'

    message.answer(report(date, message))


@router.message(Command(commands='on_date_report'))
async def on_date_report_command(message: types.Message):
    #date =
    pass

    #message.answer(report(date, message))



# TODO: create a chat leave command, should delete any info of-group info
# TODO: create a new_schedule_command

