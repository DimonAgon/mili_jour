#aiogram
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
#aiogram

#aiogram_forms
from .forms.dispatcher import dispatcher as forms_dispatcher
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
journal_router = Router()
presence_poll_router = Router()
registration_router = Router()
journal_registration_subrouter = Router()
registration_router.include_routers(journal_registration_subrouter)
commands_router.include_routers(registration_router, journal_router)
dp.include_routers(commands_router, presence_poll_router)
forms_dispatcher.attach(dp)


