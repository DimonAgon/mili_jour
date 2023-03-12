import asyncio
from django.core.management.base import BaseCommand
from bot.handlers.dispatcher import dp, bot


class Command(BaseCommand):
    help = "Implemented to a Django application Telegram bot setup command"

    async def handle_async(self, *args, **options):
        await dp.start_polling(bot)

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.handle_async(*args, **options))

