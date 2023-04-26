
from .models import *
from .forms import *

from channels.db import database_sync_to_async

from typing import Type

import datetime

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
def initiate_today_entries(today, group_id):
    if not JournalEntry.objects.filter(date=today).exists():
        journal = Journal.objects.get(external_id=group_id)
        profiles = Profile.objects.filter(journal=journal)
        ordered_profiles = profiles.order_by('ordinal')

        for p in ordered_profiles: add_journal_entry({'journal': journal, 'profile': p, 'date': today, 'is_present': False})


@database_sync_to_async
def on_lesson_view(lesson, user_id, date):
    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=date)
    corresponding_entry.lesson = lesson
    corresponding_entry.is_present = True
    corresponding_entry.save()

@database_sync_to_async
def if_absent_view(user_id, date):
    profile = Profile.objects.get(external_id=user_id)
    journal = profile.journal
    corresponding_entry = JournalEntry.objects.get(journal=journal, profile=profile, date=date)
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
