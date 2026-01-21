import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ВСТАВЬ ТОЧНЫЙ ТОКЕН НИЖЕ ===
TELEGRAM_TOKEN = "8464793187:AAFBxGo_29XvDp543IPsPydWC6D0xR4qDd0" # ПРОВЕРЬ ЭТОТ ТОКЕН ЕЩЕ РАЗ
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
# ===============================

# Настройка Gemini 1.5 (исправлено с gemini-pro)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ Бот работает! Напиши матч для прогноза.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = f"Дай краткий футбольный прогноз на матч: {message.text}"
        response = model.generate_content(prompt)
        await message.answer(response.text if response.text else "ИИ не ответил.")
    except Exception as e:
        logging.error(f"Ошибка ИИ: {e}")
        await message.answer("Ошибка в работе ИИ.")

async def main():
    # Эта строка ОЧЕНЬ важна, она убирает старые ошибки подключения
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> БОТ ЗАПУЩЕН И ГОТОВ <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
