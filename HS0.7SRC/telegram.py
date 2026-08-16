import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

def run_bot(api_key, match_request_func, model):
    bot = Bot(api_key)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message):
        await message.answer(f"модель: {model}")

    @dp.message()
    async def echo(message: Message):
        for response in match_request_func(message.text):
            response, state = response
            await message.answer(response)

    async def main():
        await dp.start_polling(bot)

    try:
        asyncio.run(main())
    except KeyboardInterrupt: 
        return "[red]The bot has stopped working.[/red]"
