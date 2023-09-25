#aiogram
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
#aiogram

#aiogram_forms
from aiogram_forms import dispatcher as forms_distpatcher
#aiogram_forms

#django
from django.core.exceptions import PermissionDenied
from django.conf import settings
#django

#bot

#bot

TOKEN = settings.TELEGRAM_BOT_API_KEY

storage = MemoryStorage


bot = Bot(token=TOKEN)
dp = Dispatcher()#storage=storage)
commands_router = Router()
reports_router = Router()
presence_poll_router = Router()
registration_router = Router()
dp.include_routers(commands_router, reports_router, presence_poll_router, registration_router)
forms_distpatcher.attach(dp)


