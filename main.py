import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# ТВОИ КЛЮЧИ (ПРОВЕРЕНЫ)
TELEGRAM_TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка ИИ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("⚽️ Бот запущен! Напиши матч, например: Реал - Барселона")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = f"Ты футбольный аналитик. Дай краткий прогноз на матч: {message.text}. Напиши вероятный счет."
        response = model.generate_content(prompt)
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не смог составить ответ.")
    except Exception as e:
        # Если ошибка, бот напишет её в чат
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    # Очистка очереди обновлений
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> БОТ ВКЛЮЧЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        
