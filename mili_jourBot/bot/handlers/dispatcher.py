#aiogram
from aiogram import Bot, Dispatcher, Router
#aiogram

#django
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.conf import settings
#django

#pyTelegramBotAPI
from telebot import TeleBot
#pyTelegramBotAPI

#bot

#bot

TOKEN = settings.TELEGRAM_BOT_API_KEY


bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

