
from .models import *
from .forms import *
from .infrastructure.enums import *

from channels.db import database_sync_to_async

from typing import Type

import datetime

import prettytable

import regex #TODO: swap regex to re, where possible


@database_sync_to_async
def add_superuser(user_id):
    new_superuser = Superuser.objects.create(external_id=user_id)
    new_superuser.save()


@database_sync_to_async
def add_profile(data, user_id):
    initial = data
    initial['external_id'], initial['journal'] = user_id, Journal.objects.get(name=data['journal'])

    if Profile.objects.filter(external_id=user_id).exists():
        Profile.objects.get(external_id=user_id).delete()

    new_profile = Profile.objects.create(**initial)
    new_profile.save()
    Profile.objects.get(external_id=user_id)


@database_sync_to_async
def delete_profile(user_id):
    Profile.objects.get(external_id=user_id).delete()


@database_sync_to_async
def add_journal(data, group_id):
    initial = data
    initial['external_id'] = group_id

    if Journal.objects.filter(external_id=group_id).exists():
        Journal.objects.get(external_id=group_id).delete()

    new_journal = Journal.objects.create(**initial)
    new_journal.save()
    Journal.objects.get(external_id=group_id)


@database_sync_to_async
def delete_journal(group_id):
    Journal.objects.get(external_id=group_id).delete()


def add_journal_entry(initial):

    new_journal_entry = JournalEntry.objects.create(**initial)
    new_journal_entry.save()


@database_sync_to_async
def get_journal_by_name_async(journal_name):
    journal = Journal.objects.get(name=journal_name)
    return journal

@database_sync_to_async
def get_journal_by_external_id_async(journal_external_id):
    journal = Journal.objects.get(external_id=journal_external_id)
    return journal

@database_sync_to_async
def get_all_journal_profiles(journal):
    return Profile.objects.filter(journal=journal)


@database_sync_to_async
def initiate_today_entries(today, group_id, lesson=None, mode=default):
    journal = Journal.objects.get(external_id=group_id)
    try: report_parameters = ReportParameters.objects.get(journal=journal, date=today)
    except Exception: pass
    profiles = Profile.objects.filter(journal=journal)

    try:
        report_parameters

        if mode == PresenceMode.LIGHT_MODE:
            if (old_mode:= report_parameters.mode) != mode:
                if JournalEntry.objects.filter(journal=journal, date=today).exists():
                    earliest_lesson_entries = \
                        set(JournalEntry.objects.filter(journal=journal, date=today, profile=profile, is_present=True).order_by('lesson').first()
                         for profile in profiles)

                    to_delete_entries =\
                        set(JournalEntry.objects.filter(journal=journal, date=today)) - set(earliest_lesson_entries)
                    for entry in to_delete_entries: entry.delete()

                    no_entry_profiles = set(profiles) - set(e.profile for e in earliest_lesson_entries)

            elif JournalEntry.objects.filter(journal=journal, date=today).exists(): return

        else:
            existing_lesson_entries_profiles = None
            if JournalEntry.objects.filter(journal=journal, date=today, lesson=lesson).exists():
                existing_lesson_entries = JournalEntry.objects.filter(journal=journal, date=today, lesson=lesson)
                if existing_lesson_entries.count() == int(journal.strength): return

                else:
                    existing_lesson_entries_profiles = {e.profile for e in existing_lesson_entries}

            no_entry_profiles = profiles if not existing_lesson_entries_profiles else set(profiles) - existing_lesson_entries_profiles

        for p in no_entry_profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'lesson': lesson})
    except Exception:
        for p in profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'lesson': lesson})


@database_sync_to_async
def process_user_on_lesson_presence(is_present, user_id):
    now = datetime.datetime.now() #TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    lesson = Schedule.lesson_match(now_time)
    if not lesson:
        after_recess_time = (now + Schedule.recess).time()
        lesson = Schedule.lesson_match(after_recess_time) #If user voted during recess

    if lesson:
        profile = Profile.objects.get(external_id=user_id)
        journal = profile.journal
        report = ReportParameters.objects.get(date=now_date, journal=journal)
        mode = report.mode
        if not mode == PresenceMode.LIGHT_MODE:
            corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=now_date, lesson=lesson)
        else:
            corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=now_date)

        corresponding_entry.lesson = lesson

    if is_present:
        corresponding_entry.is_present = True
        corresponding_entry.save()

    else:
        corresponding_entry.is_present = False
        corresponding_entry.save()


@database_sync_to_async
def amend_statuses(date, group_id):
    journal = Journal.objects.get(external_id=group_id)
    journal_profiles = Profile.objects.filter(journal=journal)

    for profile in journal_profiles:
        on_date_profile_entries = JournalEntry.objects.filter(date=date, profile=profile)
        ordered_on_date_profile_entries = on_date_profile_entries.order_by('-lesson')

        most_relevant_status = None

        for entry in ordered_on_date_profile_entries:
            entry_status = entry.status
            if entry_status: most_relevant_status = entry_status
            else:
                entry.status = most_relevant_status
                entry.save()


@database_sync_to_async
def on_lesson_presence_check(user_id):
    profile = Profile.objects.get(external_id=user_id)
    today = datetime.datetime.now().date()
    current_lesson = Schedule.lesson_match(datetime.datetime.now().time())
    on_lesson_entry = JournalEntry.objects.get(profile=profile, lesson=current_lesson, date=today)
    presence = on_lesson_entry.is_present

    return presence


@database_sync_to_async
def set_status(data, user_id, lesson=None): #TODO: if today status: status = today status. return
    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    now = datetime.datetime.now()
    today = now.date()
    now_time = now.time()
    status = data['status']
    current_lesson = Schedule.lesson_match(now_time)
    report_parameters = ReportParameters.objects.get(journal=journal, date=today)
    mode = report_parameters.mode
    if mode == PresenceMode.LIGHT_MODE:
        entry = JournalEntry.objects.get(journal=journal, profile=profile, date=today)

    else:
        lesson = current_lesson
        entry = JournalEntry.objects.get(journal=journal, profile=profile, date=today, lesson=lesson)
    entry.status = status
    entry.save()


@database_sync_to_async
def initiate_today_report(today, group_id, lessons, mode=default):
    journal = Journal.objects.get(external_id=group_id)

    if not ReportParameters.objects.filter(date=today, journal=journal, lessons=lessons, mode=mode).exists():

        if ReportParameters.objects.filter(date=today, journal=journal).exists():
            if ReportParameters.objects.filter(date=today, journal=journal, mode=mode).exists():
                corresponding_report = ReportParameters.objects.get(date=today, journal=journal)
                corresponding_report.lessons = lessons
                corresponding_report.save()

            if ReportParameters.objects.filter(date=today, journal=journal, lessons=lessons).exists():
                corresponding_report = ReportParameters.objects.get(date=today, journal=journal)
                corresponding_report.mode = mode
                corresponding_report.save()

            else:
                corresponding_report = ReportParameters.objects.get(date=today, journal=journal)
                corresponding_report.lessons = lessons
                corresponding_report = ReportParameters.objects.get(date=today, journal=journal)
                corresponding_report.mode = mode
                corresponding_report.save()

        else:
            journal = Journal.objects.get(external_id=group_id)
            report = ReportParameters.objects.create(journal=journal, date=today, lessons=lessons, mode=mode)
            report.save()


@database_sync_to_async
def report_table(report) -> Type[prettytable.PrettyTable]:
    journal = report.journal
    report_date = report.date
    entries = JournalEntry.objects.filter(journal=journal, date=report_date)
    lessons = report.lessons_integer_list
    wp_mode = report.mode
    headers = ["Студент"] + [l for l in lessons]
    table = prettytable.PrettyTable(headers)
    table.border = False

    if wp_mode == PresenceMode.LIGHT_MODE:
        for entry in entries:
            profile = entry.profile

            if entry.is_present:
                appeared_at = entry.lesson
                appeared_at_lesson_index = lessons.index(appeared_at)
                lessons_quantity = len(lessons)
                presence = ["н" if i < appeared_at_lesson_index else "·" for i in range(lessons_quantity)]
            else:
                presence = ["н" for l in lessons]

            table.add_row([regex.match(r'\p{Lu}\p{Ll}+', str(profile)).group(0), *presence])

    else:
        journal_profiles = Profile.objects.filter(journal=journal)
        ordered_profiles = journal_profiles.order_by('ordinal')
        for profile in ordered_profiles:
            profile_entries = entries.filter(profile=profile)
            ordered_profile_entries = profile_entries.order_by('lesson')

            row = [regex.match(r'\p{Lu}\p{Ll}+', str(profile)).group(0)]

            for entry in ordered_profile_entries:
                presence = entry.is_present
                row.append("·" if presence else "н")

            try: table.add_row(row)
            except:
                missing_entries_count = len(headers) - len(row)
                for i in range(missing_entries_count): row.append("_")
                table.add_row(row)

    return table


def all_entries_empty(entries):
    if not entries.filter(is_present=True) and not entries.filter(is_present=False):
        return True

def filled_absence_cell_row(entry, absence_cell):
    status = entry.status
    last_name = regex.match(r'\p{Lu}\p{Ll}+', str(entry.profile)).group(0)
    absence_cell.append(last_name if not status else f"{last_name}— {status}")
    return absence_cell

def filled_absence_cell(entries, wp_mode, lesson):
    absence_cell = []

    if wp_mode == PresenceMode.LIGHT_MODE:
        for entry in entries:
            entry_lesson = entry.lesson
            if not entry_lesson or entry_lesson > lesson:
                absence_cell = filled_absence_cell_row(entry, absence_cell)

    else:
        for entry in entries:
            if not entry.is_present:
                absence_cell = filled_absence_cell_row(entry, absence_cell)

    return absence_cell

def summary_row(wp_mode, report_mode, lesson, entries, journal_strength, report_date=None, today=None, now_time=None):

    if wp_mode == PresenceMode.LIGHT_MODE:

        absence_cell = filled_absence_cell(entries, wp_mode, lesson)

        present_count = int(journal_strength) - len(absence_cell)
        return [lesson, journal_strength, present_count, "\n".join(absence_cell)]

    else:
        lesson_entries = entries.filter(lesson=lesson)

        absence_cell = []

        lesson_time_interval = Schedule.lessons_intervals[lesson]
        lesson_start_time = lesson_time_interval.lower
        lesson_end_time = lesson_time_interval.upper

        if not report_mode == ReportMode.TODAY and today > report_date:

            absence_cell = filled_absence_cell(lesson_entries, wp_mode, lesson)

            absent_count = len(absence_cell)
            present_count = int(journal_strength) - absent_count
            presence_indicator = present_count

        else:

            if now_time > lesson_start_time:

                absence_cell = filled_absence_cell(lesson_entries, wp_mode, lesson)

                absent_count = len(absence_cell)
                present_count = int(journal_strength) - absent_count

                if present_count == 0:
                    if now_time < lesson_end_time:
                        if all_entries_empty(lesson_entries) or not lesson_entries:
                            presence_indicator = '?'
                        else:
                            presence_indicator = present_count
                    else:
                        presence_indicator = present_count
                else:
                    presence_indicator = present_count
            else:
                presence_indicator = '?'

        return [lesson, journal_strength, presence_indicator, "\n".join(absence_cell)]

@database_sync_to_async
def report_summary(report, report_mode) -> Type[prettytable.PrettyTable]:
    journal = report.journal
    journal_strength = journal.strength
    report_date = report.date
    entries = JournalEntry.objects.filter(journal=journal, date=report_date)
    lessons = report.lessons_integer_list
    wp_mode = report.mode #TODO COSMETICAL: use WhoSPresent(report.mode) instead
    headers = ["Зан.", "Сп.", "Пр.", "Відсутні"]
    summary = prettytable.PrettyTable(headers)

    if wp_mode == PresenceMode.LIGHT_MODE:
        for lesson in lessons:
            lesson_row = summary_row(wp_mode, report_mode, lesson, entries, journal_strength)
            summary.add_row(lesson_row)
    else:
        ordered_entries = entries.order_by('profile__ordinal')

        now = datetime.datetime.now()
        now_time = now.time()
        today = now.date()

        for lesson in lessons:
            lesson_row = summary_row(wp_mode, report_mode, lesson, ordered_entries, journal_strength, report_date, today, now_time)
            summary.add_row(lesson_row)

    return summary


@database_sync_to_async
def get_on_mode_report(group_id, mode, specified_date: datetime=None) -> Type[ReportParameters]:
    journal = Journal.objects.get(external_id=group_id)

    match mode:
        case ReportMode.TODAY:
            date = datetime.datetime.today().date()
            corresponding_report = ReportParameters.objects.get(date=date, journal=journal)

        case ReportMode.LAST:
            journal_reports = ReportParameters.objects.filter(journal=journal)
            corresponding_report = journal_reports.order_by('date')[len(journal_reports) - 1] # bare -1 is not supported

        case ReportMode.ON_DATE:
            corresponding_report = ReportParameters.objects.get(date=specified_date, journal=journal)

    return corresponding_report

async def get_journal_dossier(group_id):
    journal = Journal.objects.get(external_id=group_id)
    headers = ["№", "Ім'я"]
    table = prettytable.PrettyTable(headers)
    for profile in await get_all_journal_profiles(journal):
        table.add_row([profile.ordinal, profile.name])

    return table


@database_sync_to_async
def add_presence_poll(poll_id):
    PresencePoll.objects.create(external_id=poll_id)

@database_sync_to_async
def delete_presence_poll(poll_id):
    poll = PresencePoll.objects.get(external_id=poll_id)
    poll.delete()
