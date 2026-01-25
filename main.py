import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# ТВОИ КЛЮЧИ
TELEGRAM_TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("⚽️ Бот запущен! Напиши название матча.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = f"Ты футбольный аналитик. Дай краткий прогноз на матч: {message.text}. Кто победит и какой счет?"
        response = model.generate_content(prompt)
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не выдал текст. Попробуй другой матч.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    # ЭТОТ БЛОК УБИВАЕТ ВСЕ КОНФЛИКТЫ
    print("Очистка очереди и старых сессий...")
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(5) # Даем Telegram 5 секунд, чтобы он закрыл все старые окна
    
    print(">>> БОТ ВКЛЮЧЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
        
