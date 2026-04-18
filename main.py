import os
import asyncio
import feedparser
import requests
from newspaper import Article
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("BOT_TOKEN")
USER_ID = "@nnn_eeeoooo"
RSS_URL = "https://ria.ru/export/rss2/archive/index.xml"

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# --- ФУНКЦИЯ НОВОСТЕЙ ---
def get_full_news():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries: return "Новостей нет."
    link = feed.entries[0].link
    try:
        article = Article(link, language='ru')
        article.download(); article.parse()
        return f"🔔 **{article.title}**\n\n{article.text[:3500]}\n\n📍 _Источник: РИА Новости_"
    except:
        return f"🔔 **{feed.entries[0].title}**\n\n{feed.entries[0].description}"

# --- ФУНКЦИЯ КУРСОВ И ПОГОДЫ ---
def get_daily_info():
    # Курсы валют (через открытое API)
    try:
        rates = requests.get("https://open.er-api.com/v6/latest/USD").json()["rates"]
        usd = round(rates["RUB"], 2)
        # Крипта (пример для BTC)
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()["bitcoin"]["usd"]
        finance = f"💰 **Курсы валют:**\n💵 USD: {usd}₽\n₿ BTC: ${btc:,}"
    except:
        finance = "💰 Курсы временно недоступны"

    # Погода (простой парсинг)
    weather_text = "🌡 **Погода на сегодня:**"
    cities = {"Москва": "Moscow", "Волгоград": "Volgograd", "Красноярск": "Krasnoyarsk"}
    for name, eng in cities.items():
        try:
            w = requests.get(f"https://wttr.in/{eng}?format=%t+%C&lang=ru").text
            weather_text += f"\n📍 {name}: {w}"
        except:
            weather_text += f"\n📍 {name}: нет данных"
    
    return f"{finance}\n\n{weather_text}"

# --- ЗАДАЧИ ДЛЯ ПЛАНИРОВЩИКА ---
async def send_news():
    try:
        await bot.send_message(USER_ID, get_full_news(), parse_mode="Markdown")
    except Exception as e: print(f"Ошибка новости: {e}")

async def send_daily():
    try:
        await bot.send_message(USER_ID, get_daily_info(), parse_mode="Markdown")
    except Exception as e: print(f"Ошибка дайджеста: {e}")

async def main():
    # 1. Новости каждые 3 часа
    scheduler.add_job(send_news, "interval", hours=3)
    
    # 2. Погода и валюты каждое утро (например, в 08:00 по Москве)
    # Для теста сейчас отправим один раз через 10 секунд после запуска:
    scheduler.add_job(send_daily, "cron", hour=8, minute=0)
    # ^ Удали эту строку выше после теста и раскомментируй нижнюю:
    # scheduler.add_job(send_daily, "cron", hour=8, minute=0)

    scheduler.start()
    print("Бот запущен! Ждем публикаций...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
