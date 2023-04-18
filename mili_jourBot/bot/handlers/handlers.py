
from aiogram import F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup


from .dispatcher import dp, router, bot
from ..models import *
from ..forms import *
from ..views import *

import datetime
import portion as P

import  prettytable

import asyncio


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
                    "\n/register– реєструвати профілю" \
                    "\n/register_journal– створити журнал відвідувань" \
                    "\n/cancel_registration– відмінити реєстрацію" \
                    "\n/who_s_present– створити опитування щодо присутності" \
                    "\n/today_report– викликати звіт за сьогоднішній день" \
                    "\n/last_report– викликати останній звіт" \
                    "\n/on_date_report– викликати звіт за датою"

    # TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


async def initiate_today_entries(today, journal): # TODO: the better choice may be to call function on every study day
    profiles = Journal.objects.filter() #TODO: use stat-machine for better-performance
    ordered_profiles = profiles.order_by('ordinal')

    for p in ordered_profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'is_present': False})


@router.message(Command(commands='who_s_present'))  # TODO: add an enum for zoom-mode, add an enum for schedule mode
async def who_s_present_command(message: types.Message, state: FSMContext):  # Checks who is present
    now = datetime.datetime.now()
    today = now.date()
    deadline_time = datetime.time(hour=17, minute=5)
    deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute)
    till_deadline = deadline - now
    question = str(today) + " Присутні"
    group_id = message.chat.id
    journal = Journal.objects.filter(external_id=group_id) # TODO: adapt django functions to async

    await initiate_today_entries(today)
    poll_message = await message.answer_poll(question=question, options=["Я", "Відсутній"], type='quiz', correct_option_id=0, is_anonymous=False, allows_multiple_answers=False, protect_content=True) # TODO: forbid re-answering

    await asyncio.sleep(300)  # till_deadline.total_seconds())
    await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)


class Schedule: #Do not try to deceive the poll
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
        # TODO: adapt django functions to async
        user_id = poll_answer.user.id
        profile = Profile.objects.get(external_id=user_id)
        journal = Journal.objects.get(name=profile.journal)
        corresponding_entry = JournalEntry(journal=journal, profile=profile, date=now_date)
        corresponding_entry.lesson, corresponding_entry.is_present = lesson, True
        corresponding_entry.save()


@router.message(Command(commands='register'), F.chat.type.in_({'private'}))
async def register_command(message: types.Message, forms: FormsManager):

    await message.reply(text='ініціюю реєстрацію')
    await asyncio.sleep(3)

    await forms.show('profileform')



@router.message(Command(commands='register_journal'), F.chat.type.in_({'group'}))
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

async def report(date, message:types.Message):
    table = prettytable.PrettyTable(["Студент", "Заняття №", "Присутність"])
    group_id = message.chat.id
    journal = Journal.objects.get(external_id=group_id)
    if date == 'last': entries = JournalEntry.objects.filter(journal=journal).latest()
    else: entries = JournalEntry.objects.filter(journal=journal, date=date)
    # TODO: adapt django functions to async
    for entry in entries:
        profile = entry.profile

        if entry.is_present: presence = "·"
        else: presence = "н/б"

        table.add_row(str(profile), entry.lesson, presence)


@router.message(Command(commands='today_report'))
async def today_report_command(message: types.Message):
    today = datetime.datetime.today().date()

    message.answer(report(today, message))


@router.message(Command(commands='last_report'))
async def last_report_command(message: types.Message):
    date = 'last'

    message.answer(report(date, message))


@router.message(Command(commands='on_date_report'))
async def on_date_report_command(message: types.Message):
    date = None

    message.answer(report(date, message))



# TODO: create a chat leave command, should delete any info of-group info
# TODO: create a new_schedule_command

