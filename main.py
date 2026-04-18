import os
import asyncio
import feedparser
import requests
import pytz
from newspaper import Article
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройки
TOKEN = os.getenv("BOT_TOKEN")
USER_ID = "@nnn_eeeoooo"
RSS_URL = "https://ria.ru/export/rss2/archive/index.xml"
# Устанавливаем часовой пояс Красноярска
KRASNOYARSK_TZ = pytz.timezone("Asia/Krasnoyarsk")

bot = Bot(token=TOKEN)
dp = Dispatcher()
# Указываем планировщику работать по времени Красноярска
scheduler = AsyncIOScheduler(timezone=KRASNOYARSK_TZ)

# --- 1. ФУНКЦИЯ ПОЛНЫХ НОВОСТЕЙ ---
def get_full_news():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries: return "Новостей пока нет."
    link = feed.entries[0].link
    try:
        article = Article(link, language='ru')
        article.download()
        article.parse()
        return f"🔔 **{article.title}**\n\n{article.text[:3500]}\n\n📍 _Источник: РИА Новости_"
    except:
        return f"🔔 **{feed.entries[0].title}**\n\n{feed.entries[0].description}"

# --- 2. ФУНКЦИЯ КУРСОВ И ПОГОДЫ ---
def get_daily_report():
    # Погода (Красноярск, Москва, Волгоград)
    weather_text = "🌡 **ПОГОДА НА СЕГОДНЯ**"
    cities = {"Красноярск": "Krasnoyarsk", "Москва": "Moscow", "Волгоград": "Volgograd"}
    for name, eng in cities.items():
        try:
            res = requests.get(f"https://wttr.in/{eng}?format=%t+%C&lang=ru").text
            weather_text += f"\n📍 {name}: {res.strip()}"
        except: weather_text += f"\n📍 {name}: ошибка данных"

    # Курсы валют и крипты
    try:
        rates = requests.get("https://open.er-api.com/v6/latest/USD").json()["rates"]
        usd = round(rates["RUB"], 2)
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()["bitcoin"]["usd"]
        finance_text = f"💰 **КУРСЫ ВАЛЮТ**\n💵 Доллар: {usd}₽\n₿ Bitcoin: ${btc:,}"
    except:
        finance_text = "💰 Курсы временно недоступны"

    return f"{weather_text}\n\n{finance_text}"

# --- ЗАДАЧИ ПО РАСПИСАНИЮ ---
async def job_news():
    text = get_full_news()
    await bot.send_message(USER_ID, text, parse_mode="Markdown")

async def job_daily_report():
    text = get_daily_report()
    await bot.send_message(USER_ID, text, parse_mode="Markdown")

async def main():
    # Новости: каждые 30 минут
    scheduler.add_job(job_news, "interval", minutes=30)
    
    # Отчет (Погода + Валюты): каждый день в 10:00 по Красноярску
    scheduler.add_job(job_daily_report, "cron", hour=10, minute=0)

    scheduler.start()
    print("Бот запущен! Время Красноярска:", 
          asyncio.get_event_loop().time()) # Проверка в логах
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
