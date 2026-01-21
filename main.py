import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ТВОИ ПРОВЕРЕННЫЕ КЛЮЧИ ===
TELEGRAM_TOKEN = "8464793187:AAFBxGo_29XvDp543IPsPydWC6D0xR4qDd0"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
# ==============================

# Настройка актуальной модели Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ Бот готов! Напиши название матча, и я проанализирую его через Gemini 1.5.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        # Показываем, что бот думает
        await bot.send_chat_action(message.chat.id, "typing")
        
        prompt = f"Проанализируй футбольный матч и дай краткий прогноз: {message.text}"
        response = model.generate_content(prompt)
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("К сожалению, не удалось получить ответ от ИИ.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка при обращении к ИИ. Попробуй позже.")

async def main():
    # Очищаем очередь старых сообщений, чтобы не было конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> БОТ ЗАПУЩЕН НА GEMINI 1.5 FLASH <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
