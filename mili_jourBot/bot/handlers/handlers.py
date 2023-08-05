import logging
import re

import htmldocx
from aiogram import F
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.methods import GetChatAdministrators
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
from .static_text import *

import asyncio

import datetime

import docx

import tempfile, os

import random


@router.message(Command(commands='start'))
async def start_command(message: types.Message):  # Self-presentation of the bot

    await message.reply(greeting_text)


@router.message(Command(commands='help'))
async def help_command(message: types.Message):
    #TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


@router.message(Command(commands=['who_s_present', 'wp']),
                F.chat.type.in_({'group', 'supergroup'}),
                IsAdminFilter(),
                AftercommandFullCheck(allow_no_argument=False,
                                      modes=WhoSPresentMode,
                                      mode_checking=True,
                                      allow_no_mode= True,
                                      additional_arguments_checker=lessons_validator))
async def who_s_present_command(message: types.Message, command: CommandObject):  # Checks who is present
    arguments = command.args.split()

    try:
        mode, *lessons_string_list = arguments
        validate_is_mode(mode, WhoSPresentMode)

    except:
        lessons_string_list = arguments
        mode = default

    if mode in (WhoSPresentMode.LIGHT_MODE, WhoSPresentMode.NORMAL_MODE, WhoSPresentMode.HARDCORE_MODE):
        lessons = [int(e) for e in lessons_string_list]

    else:
        if lessons_string_list:
            await message.answer(no_additional_arguments_required)
            logging.error("Command initiation failed\nError: no arguments expected")
            pass

    lessons.sort()
    unique_lessons = list(set(lessons))

    now = datetime.datetime.now()
    today = now.date()
    now_time = now.time()
    date_format = NativeDateFormat.date_format
    today_string = today.strftime(date_format)

    group_id = message.chat.id

    poll_configuration = {'options': list(presence_option_to_string(o) for o in PresencePollOptions),
                           'type': 'quiz', 'correct_option_id': 0,
                           'is_anonymous': False,
                           'allows_multiple_answers': False,
                           'protect_content': True}

    if mode == WhoSPresentMode.LIGHT_MODE:
        last_lesson = unique_lessons[-1]
        last_lesson_time = Schedule.lessons_intervals[last_lesson]
        deadline_time = last_lesson_time.upper
        deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute, second=deadline_time.second)
        till_deadline = deadline - now
        question = today_string + " Присутність"
        poll_configuration.update({'question': question})

    if not mode == WhoSPresentMode.LIGHT_MODE:
        await initiate_today_report(today, group_id, unique_lessons, mode)
        for lesson in unique_lessons:

            await initiate_today_entries(today, group_id, lesson, mode)

            question = today_string + f" Заняття {str(lesson)}"
            poll_configuration.update({'question': question})

            lesson_time_interval = Schedule.lessons_intervals[lesson]
            if lesson_time_interval.contains(now_time): start_time = start_time = (now + datetime.timedelta(seconds=1)).time()
            elif now_time < lesson_time_interval.lower:  start_time = lesson_time_interval.lower
            else:
                message.answer(f"Заняття {lesson} пропущено, час заняття вичерпано")
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
            till_deadline = deadline - now #TODO: create an async scheduler
            poll_message = await message.answer_poll(**poll_configuration) #TODO: consider using poll configuration dict
            await asyncio.sleep(till_deadline.seconds)  #TODO: schedule instead
            await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)

        await amend_statuses(today, group_id)


    else:
        await initiate_today_entries(today, group_id) #TODO: the better choice may be to call function on every study day
        await initiate_today_report(today, group_id, unique_lessons)
        poll_message = await message.answer_poll(**poll_configuration)
        await asyncio.sleep(till_deadline.seconds) #TODO: schedule instead
        await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)


class AbsenceReasonStates(StatesGroup): AbsenceReason = State()

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Т'), F.chat.type.in_({'private'}))
async def absence_reason_handler_T(message: types.Message, forms: FormsManager):
    await forms.show('absenceform')

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Н'), F.chat.type.in_({'private'}))
async def absence_reason_handler_H(message: types.Message, state: FSMContext):
    await state.clear()

@router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'[^ТН]'), F.chat.type.in_({'private'}))
async def absence_reason_handler_invalid(message: types.Message, state: FSMContext):
    await message.answer(absence_reason_share_suggestion_text)

@router.poll_answer() #TODO: add a flag for vote-answer mode, add an every-lesson mode
async def who_s_present_poll_handler (poll_answer: types.poll_answer, state: FSMContext):  #TODO: add an ability to re-answer
    is_present = poll_answer.option_ids == [PresencePollOptions.Present.value]
    user_id = poll_answer.user.id

    await presence_view(is_present, user_id)

    if not is_present:
        await bot.send_message(user_id, absence_reason_share_suggestion_text)
        await state.set_state(AbsenceReasonStates.AbsenceReason)


@router.message(Command(commands='absence_reason'), F.chat.type.in_({'private'}))
async def absence_reason_command(message: types.Message, forms: FormsManager):
    user_id = message.from_user.id
    #TODO: pass the lesson if lesson is none, then answer and return
    try:
        await validate_on_lesson_presence(user_id)

    except:
        await message.answer(out_of_lesson_absence_reason_sharing_error_message)
        return

    if not await on_lesson_presence_check(user_id):
        await forms.show('absenceform')

    else:
        logging.error(f"Absence reason set is impossible, user {user_id} is present")
        await message.answer(on_present_absence_reason_sharing_error_message)
        logging.error(f"failed to set a status for user {user_id}, is_present: True")

@router.message(Command(commands='register'), F.chat.type.in_({'private'}), RegisteredExternalIdFilter(Profile))
async def register_command(message: types.Message, forms: FormsManager):

    await message.reply(text=profile_registration_text)
    await asyncio.sleep(3)

    await forms.show('profileform')


@router.message(Command(commands='register_journal'), F.chat.type.in_({'group', 'supergroup'}), IsAdminFilter(),
                RegisteredExternalIdFilter(Journal, use_chat_id=True))
async def register_journal_command(message: types.Message, forms: FormsManager):

    await message.reply(text=group_registration_text)
    await asyncio.sleep(3)

    await forms.show('journalform')


@router.message(Command(commands='cancel'))
async def cancel_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply(text=registration_canceling_text)
#TODO: reports should be able in both group and private chat


@router.message(Command(commands='today_report'), IsAdminFilter(),
                AftercommandFullCheck(allow_no_argument=True, modes=ReportMode, flag_checking=True))
async def today_report_command(message: types.Message, command: CommandObject):
    aftercommand = command.args
    if aftercommand:
        arguments = aftercommand
        flag = arguments
    else: flag = ReportMode.Flag.TEXT

    group_id = message.chat.id
    today_report = await get_report(group_id, ReportMode.TODAY)
    table = await report_table(today_report)
    summary = await report_summary(today_report, ReportMode.TODAY)

    date_format = NativeDateFormat.date_format
    date_string = today_report.date.strftime(date_format)

    await message.answer(f"Таблиця присутності, Звіт за {date_string}")

    match ReportMode.Flag(flag):

        case ReportMode.Flag.TEXT:
            await message.answer(str(table))
            await message.answer(str(summary), disable_notification=True)

        case ReportMode.Flag.DOCUMENT:
                temp_path = os.path.join(tempfile.gettempdir(), os.urandom(24).hex()) + '.docx'
                document = docx.Document()
                parser = htmldocx.HtmlToDocx()

                table_html = table.get_html_string()
                parser.add_html_to_document(table_html, document)
                document.save(temp_path)
                input_file = types.FSInputFile(temp_path)
                await message.answer_document(input_file)

                document._body.clear_content()


                summary_html = summary.get_html_string()
                parser.add_html_to_document(summary_html, document)
                document.save(temp_path)
                input_file = types.FSInputFile(temp_path)
                await message.answer_document(input_file, disable_notification=True)


@router.message(Command(commands='last_report'), IsAdminFilter(),
                AftercommandFullCheck(allow_no_argument=True, modes=ReportMode, flag_checking=True))
async def last_report_command(message: types.Message, command: CommandObject):
    aftercommand = command.args
    if aftercommand:
        arguments = aftercommand
        flag = arguments
    else: flag = ReportMode.Flag.TEXT

    group_id = message.chat.id
    last_report = await get_report(group_id, ReportMode.LAST)
    table = await report_table(last_report)
    summary = await report_summary(last_report, ReportMode.LAST)

    date_format = NativeDateFormat.date_format
    date_string = last_report.date.strftime(date_format)

    await message.answer(f"Таблиця присутності, Звіт за {date_string}")

    match ReportMode.Flag(flag):

        case ReportMode.Flag.TEXT:
            await message.answer(str(table))
            await message.answer(str(summary), disable_notification=True)

        case ReportMode.Flag.DOCUMENT:
            temp_path = os.path.join(tempfile.gettempdir(), os.urandom(24).hex()) + '.docx'
            document = docx.Document()
            parser = htmldocx.HtmlToDocx()

            table_html = table.get_html_string()
            parser.add_html_to_document(table_html, document)
            document.save(temp_path)
            input_file = types.FSInputFile(temp_path)
            await message.answer_document(input_file)

            document._body.clear_content()

            summary_html = summary.get_html_string()
            parser.add_html_to_document(summary_html, document)
            document.save(temp_path)
            input_file = types.FSInputFile(temp_path)
            await message.answer_document(input_file, disable_notification=True)


@router.message(Command(commands='on_date_report'),
                IsAdminFilter(),
                AftercommandFullCheck(allow_no_argument=False,
                                      modes=ReportMode,
                                      additional_arguments_checker=date_validator,
                                      flag_checking=True))
async def on_date_report_command(message: types.Message, command: CommandObject):
    arguments = command.args.split()

    try: date_string, flag = arguments
    except:
        date_string = arguments[0]
        flag = ReportMode.Flag.TEXT

    date_format = NativeDateFormat.date_format
    date = datetime.datetime.strptime(date_string, date_format).date()

    group_id = message.chat.id

    try:
        on_date_report = await get_report(group_id, ReportMode.ON_DATE, date)

    except: #TODO: write a decorator-validator instead
        await message.answer(on_invalid_date_report_error_message)
        logging.error(f"get report failed, no reports on {date} date")
        return

    table = await report_table(on_date_report)
    summary = await report_summary(on_date_report, ReportMode.ON_DATE)


    await message.answer(f"Таблиця присутності, Звіт за {date_string}")

    match ReportMode.Flag(flag):

        case ReportMode.Flag.TEXT:
            await message.answer(str(table))
            await message.answer(str(summary), disable_notification=True)

        case ReportMode.Flag.DOCUMENT:
            temp_path = os.path.join(tempfile.gettempdir(), os.urandom(24).hex()) + '.docx'
            document = docx.Document()
            parser = htmldocx.HtmlToDocx()

            table_html = table.get_html_string()
            parser.add_html_to_document(table_html, document)
            document.save(temp_path)
            input_file = types.FSInputFile(temp_path)
            await message.answer_document(input_file)

            document._body.clear_content()

            summary_html = summary.get_html_string()
            parser.add_html_to_document(summary_html, document)
            document.save(temp_path)
            input_file = types.FSInputFile(temp_path)
            await message.answer_document(input_file, disable_notification=True)


#TODO: create a chat leave command, should delete any info of-group info
#TODO: create a new_schedule_command

