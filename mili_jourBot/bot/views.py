
from .models import *
from .forms import *
from .infrastructure.enums import *

from channels.db import database_sync_to_async

from typing import Type

import datetime

import prettytable

import statistics

import regex

@database_sync_to_async
def add_profile(data, user_id):
    initial = data
    initial['external_id'], initial['journal'] = user_id, Journal.objects.get(name=data['journal'])

    new_profile = Profile.objects.create(**initial)
    new_profile.save()
    Profile.objects.get(external_id=user_id)


@database_sync_to_async
def add_journal(data, group_id):
    initial = data
    initial['external_id'] = group_id

    new_journal = Journal.objects.create(**initial)
    new_journal.save()
    Journal.objects.get(external_id=group_id)


def add_journal_entry(initial):

    new_journal_entry = JournalEntry.objects.create(**initial)
    new_journal_entry.save()


@database_sync_to_async
def initiate_today_entries(today, group_id, lesson=None, mode=default):
    journal = Journal.objects.get(external_id=group_id)

    if mode == WhoSPresentMode.LIGHT_MODE:
        if JournalEntry.objects.filter(journal=journal, date=today).exists(): return

    else:
        if JournalEntry.objects.filter(journal=journal, date=today, lesson=lesson).exists(): return

    profiles = Profile.objects.filter(journal=journal)
    ordered_profiles = profiles.order_by('ordinal')

    for p in ordered_profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'lesson': lesson})



@database_sync_to_async
def presence_view(is_present, user_id, lesson=None):
    now = datetime.datetime.now()# TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    lesson = Schedule.lesson_match(now_time)

    if lesson:
        profile = Profile.objects.get(external_id=user_id)
        journal = profile.journal

        corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=now_date, lesson=lesson)

    if is_present:
        corresponding_entry.lesson = lesson
        corresponding_entry.is_present = True
        corresponding_entry.save()

    else:
        corresponding_entry.lesson = None
        corresponding_entry.is_present = False
        corresponding_entry.save()

@database_sync_to_async
def get_today_status(user_id):
    profile = Profile.objects.get(external_id=user_id)
    today = datetime.datetime.today()
    profile_entries = JournalEntry.objects.filter(profile=profile, date=today)
    for entry in profile_entries:
        status = entry.status
        if status:
            return status

@database_sync_to_async
def set_status(data, user_id, lesson=None, mode=default): #TODO: if today status: status = today status. return
    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    now = datetime.datetime.now()
    today = now.date()
    now_time = now.time()
    status = data['status']
    current_lesson = Schedule.lesson_match(now_time)
    if JournalEntry.objects.filter(journal=journal, profile=profile, date=today, lesson=current_lesson).exists(): #TODO: use mode instead!
        lesson = current_lesson
    entry = JournalEntry.objects.get(journal=journal, profile=profile, date=today, lesson=lesson)
    entry.status = status
    entry.save()


@database_sync_to_async
def initiate_today_report(today, group_id, lessons):
    journal = Journal.objects.get(external_id=group_id)

    if not Report.objects.filter(date=today, journal=journal, lessons=lessons).exists():
        if Report.objects.filter(date=today, journal=journal).exists():
            corresponding_report = Report.objects.get(date=today, journal=journal)
            corresponding_report.lessons_intervals = lessons
            corresponding_report.save()

        else:
            journal = Journal.objects.get(external_id=group_id)
            report = Report.objects.create(journal=journal, date=today, lessons=lessons)
            report.save()

def filled_absence_cell(entry, absence_cell):
    status = entry.status
    last_name = regex.match(r'\p{Lu}\p{Ll}+', str(entry.profile)).group(0)
    absence_cell.append(last_name if not status else last_name + "— " + status)
    return absence_cell

@database_sync_to_async
def report_today(today, group_id, lessons, mode=default):
    journal = Journal.objects.get(external_id=group_id)
    journal_strength = journal.strength
    corresponding_report = Report.objects.get(journal=journal, date=today)
    lessons = lessons
    table = prettytable.PrettyTable(["Студент"] + [l for l in lessons])
    table.border = False
    summary = prettytable.PrettyTable(["Зан.", "Сп.", "Пр.", "Відсутні"])

    entries = JournalEntry.objects.filter(journal=journal, date=today)

    if mode == WhoSPresentMode.LIGHT_MODE:
        for entry in entries:
            profile = entry.profile

            if entry.is_present:
                appeared_at = entry.lesson
                appeared_at_lesson_index = lessons.index(appeared_at)
                lessons_quantity = len(lessons)
                presence = ["н" if i < appeared_at_lesson_index else "·" for i in range(lessons_quantity)]
            else: presence = ["н" for l in lessons]

            table.add_row([regex.match(r'\p{Lu}\p{Ll}+', str(profile)).group(0), *presence])

        for lesson in lessons:
            absence_cell = []

            for entry in entries:
                entry_lesson = entry.lesson
                if not entry_lesson or entry_lesson > lesson:
                    absence_cell = filled_absence_cell(entry, absence_cell)

            present_count = int(journal_strength) - len(absence_cell)
            summary.add_row([lesson, journal_strength, present_count, "\n".join(absence_cell)])

    else:
        profiles = Profile.objects.filter(journal=journal)
        ordered_profiles = profiles.order_by('ordinal')
        for profile in ordered_profiles:
            profile_entries = entries.filter(profile=profile)
            ordered_profile_entries = profile_entries.order_by('lesson')

            row = [regex.match(r'\p{Lu}\p{Ll}+', str(profile)).group(0)]

            for entry in ordered_profile_entries:
                presence = entry.is_present
                row.append("·" if presence else "н")

        table.add_row(row)

        ordered_entries = entries.order_by('profile__ordinal')
        for lesson in lessons:
            lesson_entries = ordered_entries.filter(lesson=lesson)
            lesson_absent_entries = lesson_entries.filter(is_present=False)
            present_count = int(journal_strength) - len(lesson_absent_entries)

            absence_cell = []

            for entry in lesson_entries:
                if not entry.is_present:
                    absence_cell = filled_absence_cell(entry, absence_cell)

            summary.add_row([lesson, journal_strength, present_count, "\n".join(absence_cell)])

    corresponding_report.date, corresponding_report.table, corresponding_report.summary = today, str(table), str(summary)
    corresponding_report.save()
    return corresponding_report

@database_sync_to_async
def get_report(date, group_id):
    journal = Journal.objects.get(external_id=group_id)
    corresponding_report = Report.objects.get(date=date, journal=journal)
    return corresponding_report