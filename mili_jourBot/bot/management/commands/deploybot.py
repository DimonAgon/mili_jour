from django.core.management.base import BaseCommand
from aiogram import executor
from bot.handlers.dispatcher import dp

class Command(BaseCommand):

    help = "Implemented to a Django application Telegram bot setup command"


    def handle(self, *args, **options):
        executor.start_polling(dp)


