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

#pyTelegramBotAPI
from telebot import TeleBot
#pyTelegramBotAPI

#bot

#bot

TOKEN = settings.TELEGRAM_BOT_API_KEY

storage = MemoryStorage


bot = Bot(token=TOKEN)
dp = Dispatcher()#storage=storage)
router = Router()
dp.include_router(router)
forms_distpatcher.attach(dp)


