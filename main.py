import os
import asyncio
import feedparser
from newspaper import Article
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("BOT_TOKEN")
USER_ID = "@nnn_eeeoooo"
RSS_URL = "https://ria.ru/export/rss2/archive/index.xml"

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

def get_full_news():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return "Новостей пока нет."
    
    link = feed.entries[0].link
    try:
        article = Article(link, language='ru')
        article.download()
        article.parse()
        title = article.title
        text = article.text[:3000] 
        return f"🔔 **{title}**\n\n{text}\n\n📍 _Источник: РИА Новости_"
    except:
        return f"🔔 **{feed.entries[0].title}**\n\n{feed.entries[0].description}"

async def send_news():
    try:
        full_text = get_full_news()
        await bot.send_message(USER_ID, full_text, parse_mode="Markdown")
        print("Полная новость отправлена!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

async def main():
    # Поставим 1 минуту для теста, потом смените на hours=3
    scheduler.add_job(send_news, "interval", minutes)
    scheduler.start()
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
