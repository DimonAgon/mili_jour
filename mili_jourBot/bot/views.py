from .models import *
from aiogram_forms import FormsManager


async def add_profile(data, user_id):

    initial = data
    initial['external_id'] = user_id

    Profile.objects.create(**initial)



