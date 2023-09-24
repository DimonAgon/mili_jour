import asyncio
from django.core.management.base import BaseCommand
from bot.handlers.dispatcher import dp, bot
from mili_jourBot import settings


class Command(BaseCommand):
    help = "Implemented to a Django application Telegram bot setup command"

    def add_arguments(self, parser):

        parser.add_argument('--debug', action='store_true', help='Enable debugging mode')

    async def handle_async(self, *args, **options):

        await dp.start_polling(bot)
        # await dp.stop
        # await bot.session.close()

    async def debug_async(self):

        debug_session_subprocess = await asyncio.create_subprocess_exec('python', 'bot/debug/debugger.py')

    def handle(self, *args, **options): #TODO: add a catch for keyboard interruption

        loop = asyncio.get_event_loop()

        if options['debug'] and settings.DEBUG:

            loop.create_task(self.debug_async())

        loop.create_task(self.handle_async())
        loop.run_forever()
