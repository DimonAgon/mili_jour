from .models import *
from .forms import *
from aiogram_forms import FormsManager
import logging


async def add_profile(data, user_id):

    try:
        initial = data
        initial['external_id'] = user_id

        Profile.objects.create(**initial)
        logging.info(f"A profile created for user_id {user_id}")

    except Exception as e:
        logging.error(f"Failed to create a profile for user_id {user_id}\nError:{e}")



async def add_journal(group_id, name, strength):

    initial = {'external_id': group_id, 'name': name, 'strength': strength}

    try:
        Journal.objects.create(**initial)
        logging.info(f"A journal created for group_id {group_id}")

    except Exception as e:
        logging.error(f"Failed to create a journal for group_id {group_id}\nError:{e}")




