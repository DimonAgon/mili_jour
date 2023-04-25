
from .models import *
from .forms import *

from channels.db import database_sync_to_async

from typing import Type

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
def set_status(data, entry: Type[JournalEntry]):
    status = data['status']

    entry.status = status
    entry.save()
