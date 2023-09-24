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

from .dispatcher import dp, commands_router, reports_router, bot
from ..models import *
from ..forms import *
from ..views import *
from .filters import *
from .middleware import *
from ..infrastructure.enums import *
from ..infrastructure import enums
from .static_text import *

import asyncio

import datetime

import docx

import tempfile, os

import random

from key_generator import key_generator

from typing import Any


reports_router.message.middleware(SuperuserGetReportCommand())

prefixes = {'🗡', '/'}

@commands_router.message(Command(commands='start')) #TODO add middleware to show help for superuser
async def start_command(message: types.Message):  # Self-presentation of the bot

    await message.reply(greeting_text)


@commands_router.message(Command(commands='help', prefix=prefixes))
async def help_command(message: types.Message):
    #TODO: on_update_info

    await message.reply(HELPFUL_REPLY)


class LessonSkippedException(Exception):
    pass

def poll_time_interval(mode, lesson=None, last_lesson=None):
    now = datetime.datetime.now()
    if mode == Presence.LIGHT_MODE:
        last_lesson_time = Schedule.lessons_intervals[last_lesson]
        if last_lesson_time.lower < now.time():
            raise LessonSkippedException

        deadline_time = last_lesson_time.upper
        deadline = now.replace(hour=deadline_time.hour, minute=deadline_time.minute, second=deadline_time.second)

    if not mode == Presence.LIGHT_MODE:
        now_time = datetime.datetime.now().time()

        lesson_time_interval = Schedule.lessons_intervals[lesson]
        if lesson_time_interval.contains(now_time): start_time = (now + datetime.timedelta(seconds=1)).time()
        elif now_time < lesson_time_interval.lower:  start_time = lesson_time_interval.lower
        else:
            raise LessonSkippedException

        end_time = lesson_time_interval.upper
        deadline = now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)


        if mode == Presence.HARDCORE_MODE:
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

        return P.openclosed(poll_time, deadline)

    return P.openclosed(now, deadline)



@commands_router.message(Command(commands=['presence', 'p'], prefix=prefixes),
                         F.chat.type.in_({'group', 'supergroup'}),
                         IsAdminFilter(),
                         AftercommandFullCheck(allow_no_argument=False,
                                      modes=Presence,
                                      mode_checking=True,
                                      allow_no_mode= True,
                                      additional_arguments_checker=lessons_validator))
async def presence_command(message: types.Message, command: CommandObject):  # Checks who is present
    arguments = command.args.split()

    try:# TODO: create and use a middleware instead
        mode, *lessons_string_list = arguments
        validate_is_mode(mode, Presence)

    except:
        lessons_string_list = arguments
        mode = default

    if mode in (Presence.LIGHT_MODE, Presence.NORMAL_MODE, Presence.HARDCORE_MODE):
        lessons = [int(e) for e in lessons_string_list]

    else:
        if lessons_string_list:
            await message.answer(no_additional_arguments_required)
            logging.error(no_arguments_logging_error_message)
            pass

    lessons.sort()
    unique_lessons = list(set(lessons))

    now = datetime.datetime.now()
    today = now.date()
    date_format = NativeDateFormat.date_format
    today_string = today.strftime(date_format)

    group_id = message.chat.id

    poll_configuration = {'options': list(presence_option_to_string(o) for o in PresencePollOptions),
                           'type': 'quiz', 'correct_option_id': 0,
                           'is_anonymous': False,
                           'allows_multiple_answers': False,
                           'protect_content': True}

    if mode == Presence.LIGHT_MODE:
        last_lesson = unique_lessons[-1]
        try:
            poll__time_interval = poll_time_interval(mode, last_lesson=last_lesson)

        except LessonSkippedException:
            await message.answer(lesson_skipped_text.format(last_lesson))
            logging.info(lesson_skipped_logging_error_message.format(last_lesson))
            return

        deadline = poll__time_interval.upper
        question = today_string + " Присутність"
        poll_configuration.update({'question': question})

    if not mode == Presence.LIGHT_MODE:
        await initiate_today_report(today, group_id, unique_lessons, mode)
        logging.info(today_report_initiated_info_message.format(group_id, mode))

        for lesson in unique_lessons:
            await initiate_today_entries(today, group_id, lesson, mode)
            logging.info(lesson_entries_initiated_info_message.format(lesson, group_id))

            try:
                poll__time_interval = poll_time_interval(mode, lesson)

            except LessonSkippedException:
                await message.answer(lesson_skipped_text.format(lesson))
                logging.info(lesson_skipped_logging_error_message.format(lesson))
                continue

            poll_time = poll__time_interval.lower
            deadline = poll__time_interval.upper

            question = today_string + f" Заняття {str(lesson)}"
            poll_configuration.update({'question': question})

            till_poll = poll_time - datetime.datetime.now()
            logging.info(on_lesson_poll_expected_info_message.format(group_id, lesson, till_poll))
            await asyncio.sleep(till_poll.seconds)
            till_deadline = deadline - datetime.datetime.now() #TODO: create an async scheduler
            poll_message = await message.answer_poll(**poll_configuration) #TODO: consider using poll configuration dict
            logging.info(lesson_poll_sent_to_group_info_message.format(lesson, group_id))
            poll_id = poll_message.poll.id
            await add_presence_poll(poll_id)
            logging.info(poll_added_info_message.format(poll_id))
            logging.info(on_lesson_poll_expected_to_stop_info_message.format(group_id, lesson, till_deadline))
            await asyncio.sleep(till_deadline.seconds)  #TODO: schedule instead
            await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)
            logging.info(lesson_poll_stopped_info_message.format(lesson, group_id))
            await delete_presence_poll(poll_id)
            logging.info(poll_deleted_info_message.format(poll_id))

        await amend_statuses(today, group_id)
        logging.info(statuses_amended_for_group_info_message.format(group_id))

    else:
        await initiate_today_entries(today, group_id, mode=mode) #TODO: the better choice may be to call function on every study day
        logging.info(today_entries_initiated_info_message.format(group_id))
        await initiate_today_report(today, group_id, unique_lessons, mode='L')
        logging.info(today_report_initiated_info_message.format(group_id, mode))
        logging.info(poll_expected_info_message.format(group_id, 0))
        poll_message = await message.answer_poll(**poll_configuration)
        logging.info(poll_sent_info_message.format(group_id, mode))
        poll_id = poll_message.poll.id
        logging.info(poll_added_info_message.format(poll_id))
        till_deadline = deadline - now
        logging.info(poll_expected_to_stop_info_message.format(group_id, till_deadline))
        await asyncio.sleep(till_deadline.seconds) #TODO: schedule instead
        await bot.stop_poll(chat_id=poll_message.chat.id, message_id=poll_message.message_id)
        logging.info(poll_deleted_info_message.format(poll_id))
        logging.info(poll_stopped_info_message.format(group_id))

    return


@commands_router.message(Command(commands='cancel', prefix=prefixes))
async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    states_canceling_messages = {AbsenceReasonStates.AbsenceReason: absence_reason_share_canceling_message,
                                 JournalStatesGroup.set_journal_name: journal_unset_message,
                                 UserInformStatesGroup.receiver_id: call_canceling_message,
                                 GroupInformStatesGroup.receiver_id: group_inform_canceling_message}

    for state_key, canceling_message in states_canceling_messages.items():
        if current_state == state_key.state:
            callback_message = canceling_message
            break

    else:
        if current_state is None:
            callback_message = no_state_message

        else:
            callback_message = registration_canceling_message

    chat_id = message.chat.id
    await state.clear()
    logging.info(data_entering_canceled_message.format(chat_id))
    await message.reply(text=callback_message)


@commands_router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Т'), F.chat.type.in_({'private'}))
async def absence_reason_handler_T(message: types.Message, forms: FormsManager):
    await forms.show('absenceform')

@commands_router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'Н'), F.chat.type.in_({'private'}))
async def absence_reason_handler_H(message: types.Message, state: FSMContext):
    await state.clear()

@commands_router.message(AbsenceReasonStates.AbsenceReason, F.text.regexp(r'[^ТН]'), F.chat.type.in_({'private'}))
async def absence_reason_handler_invalid(message: types.Message, state: FSMContext):
    await message.answer(absence_reason_share_suggestion_text)

@commands_router.poll_answer(PresencePollFilter()) #TODO: add a flag for vote-answer mode, add an every-lesson mode
async def presence_handler (poll_answer: types.poll_answer, state: FSMContext):  #TODO: add an ability to re-answer
    is_present = poll_answer.option_ids == [PresencePollOptions.Present.value]
    user_id = poll_answer.user.id

    logging.info(poll_answer_info_message.format(poll_answer.option_ids, is_present, user_id))
    await process_user_on_lesson_presence(is_present, user_id)
    logging.info(presence_set_for_user_info_message.format(user_id))

    if not is_present:
        await bot.send_message(user_id, absence_reason_share_suggestion_text)
        await state.set_state(AbsenceReasonStates.AbsenceReason)
        logging.info(absence_reason_input_suggested_logging_info_message.format(user_id))


@commands_router.message(Command(commands=['absence_reason', 'ar'], prefix=prefixes), F.chat.type.in_({'private'}))
async def absence_reason_command(message: types.Message, forms: FormsManager):
    user_id = message.from_user.id
    #TODO: pass the lesson if lesson is none, then answer and return
    try:
        await validate_on_lesson_presence(user_id)

    except:
        await message.answer(out_of_lesson_absence_reason_sharing_error_message)
        return

    if not await on_lesson_presence_check(user_id):
        logging.info(absence_reason_form_initiated_info_message.format(user_id))
        await forms.show('absenceform')

    else:
        await message.answer(on_present_absence_reason_sharing_error_message)
        logging.error(absence_reason_set_impossible_error_message.format(user_id))


@commands_router.message(SuperuserKeyStates.key, F.chat.type.in_({'private'}))
async def super_user_registrator(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    authentic_key = await state.get_data()

    try:
        validate_super_user_key(message.text, authentic_key['key'], user_id)
    except:
        await message.answer(key_is_unauthentic_text)
        return

    try:
        await add_superuser(user_id)
        await message.answer(text=superuser_form_callback_message)
        logging.info(superuser_created_info_message.format(user_id))

    except Exception as e:
        await message.answer(text=on_registration_fail_text)
        logging.error(superuser_creation_error_message.format(user_id, e))


@commands_router.message(Command(commands='register_superuser', prefix=prefixes),
                         F.chat.type.in_({'private'}),
                         RegisteredExternalIdFilter(Superuser))
async def register_superuser_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logging.info(superuser_registration_form_initiated_info_message.format(user_id))
    await message.reply(text=profile_registration_text)
    await asyncio.sleep(3)

    key = key_generator.generate().get_key()

    await state.set_state(SuperuserKeyStates.key)
    await state.update_data(key=key)
    await message.answer(superuser_key_field_message)
    logging.info(superuser_key_info_message.format(user_id, key))


@commands_router.message(Command(commands='register', prefix=prefixes),
                         F.chat.type.in_({'private'}),
                         RegisteredExternalIdFilter(Profile))
async def register_command(message: types.Message, forms: FormsManager):
    user_id = message.from_user.id
    logging.info(profile_registration_form_initiated_info_message.format(user_id))
    await message.reply(text=profile_registration_text)
    await asyncio.sleep(3)

    await forms.show('profileform')


@commands_router.message(Command(commands='register_journal', prefix=prefixes),
                         F.chat.type.in_({'group', 'supergroup'}),
                         IsAdminFilter(),
                         RegisteredExternalIdFilter(Journal, use_chat_id=True))
async def register_journal_command(message: types.Message, forms: FormsManager):
    chat_id = message.chat.id
    logging.info(journal_registration_form_initiated_info_message.format(chat_id))
    await message.reply(text=group_registration_text)
    await asyncio.sleep(3)

    await forms.show('journalform')


report_commands_superuser_filters_config = (F.chat.type.in_({'private'}), IsSuperUserFilter())
report_commands_group_admin_filters_config = (F.chat.type.in_({'group', 'supergroup'}), IsAdminFilter())

today_report_command_filters_config = (Command(commands=['today_report', 'tr'], prefix=prefixes),
                                       AftercommandFullCheck(allow_no_argument=True, modes=ReportMode, flag_checking=True))

@reports_router.message(*report_commands_superuser_filters_config, *today_report_command_filters_config)
@reports_router.message(*report_commands_group_admin_filters_config, *today_report_command_filters_config)
async def today_report_command(message: types.Message, command: CommandObject, set_journal_group_id=None):
    aftercommand = command.args

    if aftercommand:
        arguments = aftercommand
        flag = arguments
    else: flag = ReportMode.Flag.TEXT

    group_id = message.chat.id if not set_journal_group_id else set_journal_group_id
    try:
        today_report = await get_on_mode_report(group_id, ReportMode.TODAY)

    except Exception:
        await message.answer(invalid_parameters_report_error_message)
        logging.error(get_report_failed_error_message.format(group_id))
        return

    table = await report_table(today_report)
    summary = await report_summary(today_report, ReportMode.TODAY)

    date_format = NativeDateFormat.date_format
    date_string = today_report.date.strftime(date_format)

    logging.info(report_requested_info_message.format(group_id, "TODAY", flag))
    await message.answer(report_text.format(date_string))

    match ReportMode.Flag(flag):

        case ReportMode.Flag.TEXT:
            await message.answer(f"```{str(table)}```", 'Markdown')
            await message.answer(f"```{str(summary)}```", 'Markdown', disable_notification=True)

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


last_report_command_filters_config = (Command(commands=['last_report', 'lr'], prefix=prefixes),
                                      AftercommandFullCheck(allow_no_argument=True, modes=ReportMode, flag_checking=True))

@reports_router.message(*report_commands_superuser_filters_config, *last_report_command_filters_config)
@reports_router.message(*report_commands_group_admin_filters_config, *last_report_command_filters_config)
async def last_report_command(message: types.Message, command: CommandObject, set_journal_group_id=None):
    aftercommand = command.args

    if aftercommand:
        arguments = aftercommand
        flag = arguments
    else: flag = ReportMode.Flag.TEXT

    group_id = message.chat.id if not set_journal_group_id else set_journal_group_id

    try:
        last_report = await get_on_mode_report(group_id, ReportMode.LAST)

    except Exception:
        await message.answer(invalid_parameters_report_error_message)
        logging.error(get_report_failed_error_message.format(group_id))
        return

    table = await report_table(last_report)
    summary = await report_summary(last_report, ReportMode.LAST)

    date_format = NativeDateFormat.date_format
    date_string = last_report.date.strftime(date_format)

    logging.info(report_requested_info_message.format(group_id, "LAST", flag))
    await message.answer(report_text.format(date_string))

    match ReportMode.Flag(flag):

        case ReportMode.Flag.TEXT:
            await message.answer(f"```{str(table)}```", 'Markdown')
            await message.answer(f"```{str(summary)}```", 'Markdown', disable_notification=True)

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


on_date_report_command_filters_config = (Command(commands=['on_date_report', 'odr'], prefix=prefixes),
                                         AftercommandFullCheck(allow_no_argument=False,
                                                        modes=ReportMode,
                                                        additional_arguments_checker=date_validator,
                                                        flag_checking=True))
@reports_router.message(*report_commands_superuser_filters_config, *on_date_report_command_filters_config)
@reports_router.message(*report_commands_group_admin_filters_config, *on_date_report_command_filters_config)
async def on_date_report_command(message: types.Message, command: CommandObject, set_journal_group_id=None):
    arguments = command.args.split()

    try: date_string, flag = arguments
    except:
        date_string = arguments[0]
        flag = ReportMode.Flag.TEXT

    date_format = NativeDateFormat.date_format
    date = datetime.datetime.strptime(date_string, date_format).date()

    group_id = message.chat.id if not set_journal_group_id else set_journal_group_id

    try:
        on_date_report = await get_on_mode_report(group_id, ReportMode.ON_DATE, date)

    except: #TODO: write a decorator-validator instead
        await message.answer(invalid_parameters_report_error_message)
        logging.error(get_report_failed_error_message.format(group_id))
        return

    table = await report_table(on_date_report)
    summary = await report_summary(on_date_report, ReportMode.ON_DATE)

    logging.info(report_requested_info_message.format(group_id, "ON DATE", flag))
    await message.answer(report_text.format(date_string))

    match ReportMode.Flag(flag):

        case ReportMode.Flag.TEXT:
            await message.answer(f"```{str(table)}```", 'Markdown')
            await message.answer(f"```{str(summary)}```", 'Markdown', disable_notification=True)

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


@commands_router.message(JournalStatesGroup.setting_journal)
async def set_journal_handler(message: types.Message, state: FSMContext):
    response = message.text
    try:
        validate_journal_format(response)

    except ValidationError as e:
        error_message = e.message
        await message.answer(error_message)
        return

    try:
        await check_journal_exists(response)

    except ValidationError as e:
        error_message = e.message
        await message.answer(error_message)
        return

    set_journal_name = response

    await state.set_state(JournalStatesGroup.set_journal_name)
    await state.update_data(set_journal_name=set_journal_name)
    await message.answer(journal_set_text.format(set_journal_name))

@commands_router.message(Command(commands=['set_journal', 'sj'], prefix=prefixes),
                         F.chat.type.in_({'private'}),
                         IsSuperUserFilter())
async def set_journal_command(message: types.Message, state: FSMContext):
    await state.set_state(JournalStatesGroup.setting_journal)
    await message.answer(enter_journal_name_message)


@commands_router.message(UserInformStatesGroup.receiver_id, NoCommandFilter(), F.chat.type.in_({'private'}))
async def user_inform_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    interlocutor_id = await state.get_data()
    await bot.send_message(interlocutor_id['Interlocutor_id'], message.text)
    await state.update_data(receiver_id=user_id)

@commands_router.message(UserInformStatesGroup.call, F.chat.type.in_({'private'}))
async def user_call_handler(message: types.Message, state: FSMContext):
    response = message.text
    user_id = message.from_user.id

    @database_sync_to_async
    def get_profile_by_name(name):
        return Profile.objects.get(name=name)

    try:
        validate_name_format(response)
    except Exception:
        await message.answer(name_format_validation_error_message)
        return
    name = response
    try:
        profile = await get_profile_by_name(name)
    except Exception as e:
        print(e)
        await message.answer(profile_by_name_not_in_db_error_message)
        await state.clear()
        return

    profile_id = profile.external_id
    await state.set_state(UserInformStatesGroup.receiver_id)
    await state.update_data(Interlocutor_id=profile_id)
    await message.answer(user_inform_text.format(name))
    await bot.send_message(profile_id, inform_message)

@commands_router.message(Command(commands=['call'], prefix=prefixes),
                         F.chat.type.in_({'private'}),
                         IsSuperUserFilter())
async def call_command(message: types.Message, state: FSMContext):
    await state.set_state(UserInformStatesGroup.call)
    await message.answer(enter_profile_name_message)

async def inform_all_journal_users(journal, message_text):
    all_journal_profiles = await get_all_journal_profiles(journal)
    for profile in all_journal_profiles: await bot.send_message(profile.external_id, message_text)
    await bot.send_message(journal.external_id, message_text)


@commands_router.message(GroupInformStatesGroup.receiver_id, NoCommandFilter(), F.chat.type.in_({'private'}))
async def group_inform_handler(message: types.Message, state: FSMContext):
    journal_external_id = await state.get_data()
    journal = await get_journal_by_external_id_async(journal_external_id['receiver_id'])
    await inform_all_journal_users(journal, message.text)
    await state.clear()

@commands_router.message(GroupInformStatesGroup.call, F.chat.type.in_({'private'}))
async def group_call_handler(message: types.Message, state: FSMContext):
    response = message.text

    try:
        validate_journal_format(response)

    except Exception:
        await message.answer(journal_format_validation_error_message)
        return
    journal_name = response
    try:
        journal = await get_journal_by_name_async(journal_name)

    except Exception as e:
        print(e)
        await message.answer(journal_name_in_base_validation_error_message)
        await state.clear()
        return

    await state.set_state(GroupInformStatesGroup.receiver_id)
    await state.update_data(receiver_id=journal.external_id)
    await message.answer(group_inform_text.format(journal_name))
    await inform_all_journal_users(journal, group_inform_message)


@commands_router.message(Command(commands=['groupcall', 'gc'], prefix=prefixes),
                         F.chat.type.in_({'private'}),
                         IsSuperUserFilter())
async def group_call_command(message: types.Message, state: FSMContext):
    await state.set_state(GroupInformStatesGroup.call)
    await message.answer(enter_journal_name_message)

#TODO: reports should be able in both group and private chat


#TODO: create a chat leave command, should delete any info of-group info
#TODO: create a new_schedule_command

