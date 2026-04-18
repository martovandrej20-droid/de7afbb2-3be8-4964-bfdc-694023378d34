import os
import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
TOKEN = os.getenv("BOT_TOKEN")
USER_ID = "@nnn_eeeoooo"
bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
async def send_scheduled_message():
    try:
        await bot.send_message(USER_ID, "Привет! Это автоматическая новость 🚀")
        print("Сообщение успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
async def main():
    scheduler.add_job(send_scheduled_message, "interval", seconds=10)
    scheduler.start()
    print("Бот запущен!")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
