import asyncio
import aiohttp
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

# --- ТВОИ КЛЮЧИ ---
TELEGRAM_TOKEN = "8464793187:AAFqwp0ec_ZOIOd4Jq-AkW-CaiTiDI4PcIo"
FOOTBALL_API_KEY = "c30951a5dcb846ba9d692fe43e8120c4"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка прокси для PythonAnywhere
proxy_url = "http://proxy.server:3128"
session = AiohttpSession(proxy=proxy_url)

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Исправленные объекты (только на английском!)
bot = Bot(token=TELEGRAM_TOKEN, session=session)
dp = Dispatcher()

async def get_ai_prediction(match_info):
    prompt = f"Ты эксперт. Проанализируй матч: {match_info}. Дай прогноз на русском."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ошибка ИИ: {e}"

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("✅ ИИ-Бот готов! Нажми /predict")

@dp.message(Command("predict"))
async def predict(m: types.Message):
    await m.answer("🤖 ИИ думает...")
    # Для теста берем фиксированную пару, пока настраиваем связь
    res = await get_ai_prediction("Реал Мадрид против Барселоны")
    await m.answer(f"📊 Анализ:\n{res}")

async def main():
    print(">>> БОТ ЗАПУЩЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

