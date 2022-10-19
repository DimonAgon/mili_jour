#aiogram
from aiogram import Bot, Dispatcher
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
from ..models import Journal, JournalEntry, Profile
#bot


bot = Bot(token=settings.TELEGRAM_BOT_API_KEY)
dp = Dispatcher(bot)


