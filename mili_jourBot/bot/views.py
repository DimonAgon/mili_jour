
from .models import *
from .forms import *
from .infrastructure.enums import *

from channels.db import database_sync_to_async

from typing import Type

import datetime

import prettytable

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
def initiate_today_entries(today, group_id, lessons=list(), mode=WhoSPresentMode.LIGHT_MODE):
    if mode == WhoSPresentMode.LIGHT_MODE:
        journal = Journal.objects.get(external_id=group_id)

        if not JournalEntry.objects.filter(journal=journal, date=today).exists():
            profiles = Profile.objects.filter(journal=journal)
            ordered_profiles = profiles.order_by('ordinal')

            for p in ordered_profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'is_present': False})

@database_sync_to_async
def presence_view(is_present, user_id):
    now = datetime.datetime.now()# TODO: use time for schedule control, use date for entry's date
    now_time = now.time()
    now_date = now.date()

    if is_present:
        lesson = Schedule.lesson_match(now_time)
    else: lesson = None

    if lesson or not is_present:
        profile = Profile.objects.get(external_id=user_id)
        journal = profile.journal
        corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=now_date)

    if lesson:
        corresponding_entry.lesson = lesson
        corresponding_entry.is_present = True
        corresponding_entry.save()

    if not is_present:
        corresponding_entry.lesson = None
        corresponding_entry.is_present = False
        corresponding_entry.save()


@database_sync_to_async
def set_status(data, user_id):
    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    today = datetime.date.today()
    status = data['status']
    entry = JournalEntry.objects.get(journal=journal, profile=profile, date=today)

    entry.status = status
    entry.save()


@database_sync_to_async
def initiate_today_report(today, group_id, lessons):
    journal = Journal.objects.get(external_id=group_id)
    Report.objects.create(journal=journal, date=today, lessons=lessons)


@database_sync_to_async
def report(date, group_id, lessons, mode=WhoSPresentMode.LIGHT_MODE):
    journal = Journal.objects.get(external_id=group_id)
    #corresponding_report = Report(journal=journal, date=date)
    lessons = lessons#corresponding_report.lessons
    table = prettytable.PrettyTable(["Студент"] + [l for l in lessons])
    table.border = False
    summary = prettytable.PrettyTable(["Зан.", "Сп.", "Пр.", "Відсутні"])
    if mode == WhoSPresentMode.LIGHT_MODE:
        entries = JournalEntry.objects.filter(journal=journal, date=date)

        for entry in entries:
            profile = entry.profile

            if entry.is_present:
                appeared_at = entry.lesson
                appeared_at_lesson_index = lessons.index(appeared_at)
                lessons_quantity = len(lessons)
                presence = ["н" if i < appeared_at_lesson_index else "·" for i in range(lessons_quantity)]
            else: presence = ["н" for l in lessons]

            table.add_row([regex.match(r'\p{Lu}\p{Ll}+', str(profile)).group(0), *presence])

    #orresponding_report = Report.objects.create(journal=journal, date=date, table=str(table), summary=str(summary))
    return str(table)

@database_sync_to_async
def get_report(date, group_id):
    journal = Journal.objects.get(external_id=group_id)
    corresponding_report = Report.objects.get(date=date, journal=journal)
    return corresponding_report