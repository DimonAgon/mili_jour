
import logging

from .models import *
from .forms import *

from channels.db import database_sync_to_async

@database_sync_to_async
def add_profile(data, user_id):
    initial = data
    initial['external_id'], initial['journal'] = user_id, Journal.objects.get(name=data['journal'])

    try:

        new_profile = Profile.objects.create(**initial)
        new_profile.save()
        Profile.objects.get(external_id=user_id)
        logging.info(f"A profile created for user_id {user_id}")

    except Exception as e:
        logging.error(f"Failed to create a profile for user_id {user_id}\nError:{e}")



@database_sync_to_async
def add_journal(data, group_id):
    initial = data
    initial['external_id'] = group_id

    try:
        new_journal = Journal.objects.create(**initial)
        new_journal.save()
        Journal.objects.get(external_id=group_id)
        logging.info(f"A journal created for group_id {group_id}")

    except Exception as e:
        logging.error(f"Failed to create a journal for group_id {group_id}\nError:{e}")


def add_journal_entry(initial):

    new_journal_entry = JournalEntry.objects.create(**initial)
    new_journal_entry.save()
