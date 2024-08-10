import copy
import logging

import re

import django.db.models

from .models import *
from .forms import *
from .infrastructure.ScheduleTiming import *
from .infrastructure.enums import *
from misc.re_patterns import *
from logging_native.utilis.frame_log_track.frame_log_track import log_track_frame

from channels.db import database_sync_to_async

from typing import Type, List

import datetime

from django.utils import timezone

import prettytable

import regex #TODO: swap regex to re, where possible

#TODO: replace all async get- and delete- functions with universals

#TODO: unify code
#TODO: annotate all

@log_track_frame(total=False)
@database_sync_to_async
def add_superuser(user_id):
    new_superuser = Superuser.objects.create(external_id=user_id)
    new_superuser.save()


@log_track_frame(total=False)
@database_sync_to_async
def add_profile(attributes):
    external_id = attributes['external_id']

    if Profile.objects.filter(external_id=external_id).exists():
        Profile.objects.get(external_id=external_id).delete()

    new_profile = Profile.objects.create(**attributes)
    new_profile.save()



@log_track_frame(total=False)
@database_sync_to_async
def delete_profile(user_id):
    Profile.objects.get(external_id=user_id).delete()


@log_track_frame(total=False)
@database_sync_to_async
def add_journal(attributes):
    external_id = attributes['external_id']

    if Journal.objects.filter(external_id=external_id).exists():
        Journal.objects.get(external_id=external_id).delete()

    new_journal = Journal.objects.create(**attributes)
    new_journal.save()


@log_track_frame(total=False)
@database_sync_to_async
def delete_journal(journal: Journal=None, **journal_attributes):
    if journal:
        journal.delete()

    else:
        Journal.objects.get(**journal_attributes).delete()


@log_track_frame(total=False)
def add_journal_entry(initial):
    new_journal_entry = JournalEntry.objects.create(**initial)
    new_journal_entry.save()

@log_track_frame(total=False)
@database_sync_to_async
def add_subject(data):
    name = data['name']
    journal = data['journal']

    subject_filter_query = Subject.objects.filter(name=name)
    if subject_filter_query.exists():
        subject = subject_filter_query.first()
        subject.journals.add(journal.id)
    else:
        subject = Subject.objects.create(name=name)

    subject.save()


@log_track_frame(total=False)
def add_lesson(subject, ordinal: int) -> Lesson:
    lesson_attributes = {'subject': subject, 'ordinal': ordinal}
    lesson_filter_query = Lesson.objects.filter(subject=subject, ordinal=ordinal)
    if not lesson_filter_query.exists():
        new_lesson = Lesson.objects.create(**lesson_attributes)
        new_lesson.save()

        return new_lesson

    else:
        return lesson_filter_query.first()

@log_track_frame(total=False)
@database_sync_to_async
def add_schedule(lessons_ordinals_to_subjects_names: dict):
    new_schedule = Schedule.objects.create()
    for lesson_ordinal, subject_name in lessons_ordinals_to_subjects_names.items():
        subject = Subject.objects.get(name=subject_name)
        new_lesson = add_lesson(subject, lesson_ordinal)
        new_schedule.lessons.add(new_lesson.id)

    new_schedule.save()
    return new_schedule


@database_sync_to_async
def get_schedule_async(**schedule_attributes):
    schedule = Schedule.objects.get(**schedule_attributes)
    return schedule


@log_track_frame(total=False)
@database_sync_to_async
def add_current_schedule(attributes: dict):
    current_schedule_defining_attributes = copy.copy(attributes); schedule = current_schedule_defining_attributes.pop('schedule')
    filter_query = CurrentSchedule.objects.filter(**current_schedule_defining_attributes)
    if not filter_query.exists():
        new_current_schedule = CurrentSchedule.objects.create(**attributes)
        new_current_schedule.save()

    else:
        old_current_schedule = filter_query.first()
        if not old_current_schedule.schedule == schedule:
            setattr(old_current_schedule, 'schedule', schedule)
            old_current_schedule.save()


@database_sync_to_async
def get_current_schedule_async(attributes: dict):
    current_schedule = CurrentSchedule.objects.get(**attributes)
    return current_schedule


@database_sync_to_async
def get_journal_async(data):
    journal = Journal.objects.get(**data)
    return journal


@log_track_frame(total=False)
@database_sync_to_async
def get_profile_async(data) -> Profile:
    profile = Profile.objects.get(**data)
    return profile


@log_track_frame(total=False)
@database_sync_to_async
def get_all_journal_profiles(journal): #TODO: annotate
    return Profile.objects.filter(journal=journal)


@log_track_frame(total=False)
@database_sync_to_async
#TODO: redo to on-date entries initiation
def initiate_today_entries(today: datetime.date, journal: Journal, lesson: Lesson): #TODO: fix on less lessons reinitiation bug
    try: report_parameters = ReportParameters.objects.get(journal=journal, date=today)
    except Exception: pass
    profiles = Profile.objects.filter(journal=journal)

    try:
        report_parameters

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


@log_track_frame(total=False)
@database_sync_to_async
def process_user_on_lesson_presence(is_present, user_id):
    now = timezone.localtime(timezone.now()) #TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    current_schedule = CurrentSchedule.objects.get(journal=journal, date=now_date)
    schedule = current_schedule.schedule
    lessons: django.db.models.QuerySet = schedule.lessons.all()
    lesson_ordinal = ScheduleTiming.lesson_intervals_match(now_time)
    lesson_query = lessons.filter(ordinal=lesson_ordinal)

    if not lesson_query.exists():
        after_recess_time = (now + ScheduleTiming.recess).time()
        lesson_ordinal = ScheduleTiming.lesson_intervals_match(after_recess_time) #If user voted during recess

    lesson = lesson_query.first()

    report = ReportParameters.objects.get(date=now_date, journal=journal)
    mode = report.mode

    if not mode == PresenceMode.LIGHT_MODE:
        if lesson: #TODO remove condition, there would always be a lesson
            corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=now_date, lesson=lesson)
            corresponding_entry.lesson = lesson

        if is_present:
            corresponding_entry.is_present = True
            corresponding_entry.save()
            ...

        else:
            corresponding_entry.is_present = False
            corresponding_entry.save()
            ...

    else:
        profile_entries = JournalEntry.objects.filter(profile=profile)

        if is_present:
            for entry in profile_entries:
                if entry.lesson >= lesson:
                    entry.is_present = True

                else:
                    entry.is_present = False

                entry.save()

        else:
            for entry in profile_entries:
                entry.is_present = False
                entry.save()


@log_track_frame(total=False)
@database_sync_to_async
def amend_statuses(date, group_id):
    journal = Journal.objects.get(external_id=group_id)
    journal_profiles = Profile.objects.filter(journal=journal)

    for profile in journal_profiles:
        on_date_profile_entries = JournalEntry.objects.filter(date=date, profile=profile)
        ordered_on_date_profile_entries = on_date_profile_entries.order_by('-lesson__ordinal')

        most_relevant_status = None

        for entry in ordered_on_date_profile_entries:
            entry_status = entry.status
            if entry_status: most_relevant_status = entry_status
            else:
                entry.status = most_relevant_status
                entry.save()


@log_track_frame(total=False)
@database_sync_to_async
def on_lesson_presence_check(user_id): #TODO: move to checks.py

        profile = Profile.objects.get(external_id=user_id)
        now = timezone.localtime(timezone.now())
        today = now.date()
        current_lesson = ScheduleTiming.lesson_intervals_match(now.time())
        on_lesson_entry = JournalEntry.objects.get(profile=profile, lesson=current_lesson, date=today)
        presence = on_lesson_entry.is_present

        return presence


@log_track_frame(total=False)
@database_sync_to_async
def set_status(data, user_id, lesson=None): #TODO: if today status: status = today status. return
    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    now = timezone.localtime(timezone.now())
    today = now.date()
    now_time = now.time()
    status = data['status']
    current_lesson = ScheduleTiming.lesson_intervals_match(now_time)
    report_parameters = ReportParameters.objects.get(journal=journal, date=today)
    mode = report_parameters.mode
    if mode == PresenceMode.LIGHT_MODE:
        entry = JournalEntry.objects.get(journal=journal, profile=profile, date=today)

    else:
        lesson = current_lesson
        entry = JournalEntry.objects.get(journal=journal, profile=profile, date=today, lesson=lesson)
    entry.status = status
    entry.save()



@log_track_frame(total=False)
@database_sync_to_async
def initiate_today_report(today: datetime.date, journal: Journal, mode=default):
    report_parameters_attributes = {'journal': journal, 'date': today, 'mode': mode}
    today_report_parameters_query = ReportParameters.objects.filter(**report_parameters_attributes)
    if not today_report_parameters_query.exists():
        ReportParameters.objects.create(**report_parameters_attributes)

    else: \
defining_report_parameters_attributes = report_parameters_attributes; del defining_report_parameters_attributes['mode']; \
        today_report_parameters = today_report_parameters_query.first(); \
        today_report_parameters.mode = mode; \
        today_report_parameters.save()


@log_track_frame(total=False)
@database_sync_to_async
def make_report_table(report_parameters: ReportParameters) -> Type[prettytable.PrettyTable]:
    journal = report_parameters.journal
    report_date = report_parameters.date
    entries = JournalEntry.objects.filter(journal=journal, date=report_date)
    current_schedule = CurrentSchedule.objects.get(journal=journal, date=report_date)
    schedule = current_schedule.schedule
    lessons = schedule.lessons.all()
    lessons.order_by("ordinal")
    headers = ["Студент"] + [str(l) for l in lessons]
    table = prettytable.PrettyTable(headers)
    table.border = False

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


def all_entries_empty(entries): #TODO: move to checks.py
    if not entries.filter(is_present=True) and not entries.filter(is_present=False):
        return True

@log_track_frame(total=False)
def filled_absence_cell_row(entry, absence_cell):
    status = entry.status
    last_name = regex.match(r'\p{Lu}\p{Ll}+', str(entry.profile)).group(0)
    absence_cell.append(last_name if not status else f"{last_name}— {status}")
    return absence_cell


@log_track_frame(total=False)
def filled_absence_cell(entries):
    absence_cell = []

    for entry in entries:
        if not entry.is_present:
            absence_cell = filled_absence_cell_row(entry, absence_cell)

    return absence_cell

def summary_row(
        report_mode: Enum,
        lesson: Lesson,
        entries: django.db.models.QuerySet[JournalEntry],
        journal_strength,
        report_date: datetime.date=None,
        today: datetime.date=None,
        now_time: datetime.time=None
) -> list:
    lesson_entries = entries.filter(lesson=lesson)

    absence_cell = []

    lesson_time_interval = ScheduleTiming.lessons_intervals[lesson.ordinal]
    lesson_start_time = lesson_time_interval.lower
    lesson_end_time = lesson_time_interval.upper

    if not report_mode == ReportMode.TODAY and today > report_date:

        absence_cell = filled_absence_cell(lesson_entries)

        absent_count = len(absence_cell)
        present_count = int(journal_strength) - absent_count
        presence_indicator = present_count

    else:

        if now_time > lesson_start_time:

            absence_cell = filled_absence_cell(lesson_entries)

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

    return [str(lesson), journal_strength, presence_indicator, "\n".join(absence_cell)]
#TODO: add full table creation, separate full and narrow tables creation
#TODO: add documentary table creation
@log_track_frame(total=False)
@database_sync_to_async
def report_summary(report, report_mode) -> Type[prettytable.PrettyTable]:
    journal = report.journal
    journal_strength = journal.strength
    report_date = report.date
    entries = JournalEntry.objects.filter(journal=journal, date=report_date)
    current_schedule = CurrentSchedule.objects.get(journal=journal, date=report_date)
    schedule = current_schedule.schedule
    lessons = schedule.lessons.all()
    lessons.order_by("ordinal")
    headers = ["Зан.", "Сп.", "Пр.", "Відсутні"]
    summary = prettytable.PrettyTable(headers)

    ordered_entries = entries.order_by('profile__ordinal')

    now = timezone.localtime(timezone.now())
    now_time = now.time()
    today = now.date()

    for lesson in lessons:
        lesson_row = summary_row(report_mode, lesson, ordered_entries, journal_strength, report_date, today, now_time)
        summary.add_row(lesson_row)

    return summary


@log_track_frame(total=False)
@database_sync_to_async                       #TODO: add "journal" to function name
def get_on_mode_report(group_id, mode, specified_date: datetime=None) -> Type[ReportParameters]: #TODO: consider using journal #TODO: reannotate return type
                                            #TODO: consider move to get_journal_...-functions
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


@log_track_frame(total=False)
@database_sync_to_async
def redo_entries_by_report_row(report_row_match: Type[re.Match], group_id, date, lessons_ordinals: List[int]):
    name_part = report_row_match.group(1)
    report_marks = report_row_match.group(2)
    report_marks_split: list = report_marks.split()

    journal = Journal.objects.get(external_id=group_id)
    journal_profiles = Profile.objects.filter(journal=journal)
    for profile in journal_profiles:
        if name_part in profile.name:
            target_profile = profile
            break
    else:
        None

    if target_profile:
        on_date_profile_entries = JournalEntry.objects.filter(profile=target_profile, date=date).order_by('lesson__ordinal')
        on_date_profile_lessons_entries: list = [
            entry
            for entry in on_date_profile_entries
            if entry.lesson.ordinal in lessons_ordinals
        ]
        for mark, lesson_entry in zip(report_marks_split, on_date_profile_lessons_entries):
            if mark == '·':
                lesson_entry.is_present = True
            elif mark == 'н':
                lesson_entry.is_present = False
            else:
                lesson_entry.is_present = None
            lesson_entry.save()


@log_track_frame(total=False) #TODO: consider moving to handlers.py
async def get_journal_dossier(group_id): #TODO: check (it somehow works)
    journal = Journal.objects.get(external_id=group_id)
    headers = ["№", "Ім'я"]
    table = prettytable.PrettyTable(headers)
    for profile in await get_all_journal_profiles(journal):
        table.add_row([profile.ordinal, profile.name])

    return table


@log_track_frame(total=False)
def make_schedule_table(schedule: Schedule):
    schedule_table_headers = ["№", "Предмет"]
    schedule_table = prettytable.PrettyTable(schedule_table_headers)
    schedule_lessons = schedule.lessons.all()
    schedule_uninscribed_lessons = schedule_lessons
    schedule_uninscribed_lessons_list = list(schedule_uninscribed_lessons)
    for inscribed_lesson_ordinal in range(1, ScheduleTiming.last_lesson_ordinal):
        for lesson in schedule_uninscribed_lessons_list:
            if lesson.ordinal == inscribed_lesson_ordinal:
                on_ordinal_schedule_lesson = lesson
                break
        else:
            on_ordinal_schedule_lesson = None

        if on_ordinal_schedule_lesson:
            schedule_uninscribed_lessons_list.remove(on_ordinal_schedule_lesson)
            lesson_subject_name = on_ordinal_schedule_lesson.subject.name

        else:
            lesson_subject_name = "_"

        lesson_row = [inscribed_lesson_ordinal, lesson_subject_name]
        schedule_table.add_row(lesson_row)

    return schedule_table


@log_track_frame(total=False) #TODO: consider moving to handlers.py
async def get_on_mode_journal_current_schedule(journal: Journal, mode, specified_date: datetime.date=None):
    all_journal_current_schedules = CurrentSchedule.objects.filter(journal=journal)

    match mode:
        case ReportMode.TODAY:
            today_date = datetime.datetime.today()
            corresponding_current_schedule = all_journal_current_schedules.get(date=today_date)

        case ReportMode.LAST:
            corresponding_current_schedule = \
                all_journal_current_schedules.order_by('date')[len(all_journal_current_schedules) - 1]
            date = corresponding_current_schedule.date

        case ReportMode.ON_DATE:
             corresponding_current_schedule = all_journal_current_schedules.get(date=specified_date)

    return corresponding_current_schedule


@log_track_frame(total=False)
@database_sync_to_async
def add_presence_poll(poll_id):
    PresencePoll.objects.create(external_id=poll_id)


@log_track_frame(total=False)
@database_sync_to_async
def delete_presence_poll(poll_id): #TODO: instead set status to 'expired'
    poll = PresencePoll.objects.get(external_id=poll_id)
    poll.delete()