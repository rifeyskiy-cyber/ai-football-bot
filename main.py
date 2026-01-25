import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ТВОИ КЛЮЧИ ===
TELEGRAM_TOKEN = "8464793187:AAFJ0MQ6OaSGxEInG_Dt0Bg-vqdqtD4FbGY"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
# ==================

genai.configure(api_key=GEMINI_API_KEY)
# Используем максимально простую инициализацию модели
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ БОТ ОЖИЛ! Напиши матч.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        # Добавляем инструкцию для ИИ, чтобы он отвечал короче
        prompt = f"Ты футбольный аналитик. Дай прогноз на матч: {message.text}. Ответь кратко."
        response = model.generate_content(prompt)
        await message.answer(response.text)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Бот получил сообщение, но ИИ временно недоступен. Попробуй позже.")

async def main():
    # ОЧЕНЬ ВАЖНО: Удаляем вебхук перед запуском
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> БОТ ЗАПУЩЕН С ЧИСТОГО ЛИСТА <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
        
