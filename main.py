import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# Настройки
TELEGRAM_TOKEN = "ТВОЙ_ТОКЕН_ТУТ"
GEMINI_API_KEY = "ТВОЙ_КЛЮЧ_GEMINI_ТУТ"

# Настройка ИИ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Инициализация бота БЕЗ ПРОКСИ
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я футбольный аналитик на базе ИИ. Напиши мне название матча, и я дам прогноз.")

@dp.message()
async def handle_message(message: types.Message):
    prompt = f"Проанализируй футбольный матч и дай прогноз: {message.text}"
    response = model.generate_content(prompt)
    await message.answer(response.text)

async def main():
    print(">>> BOT IS RUNNING ON KOYEB <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
