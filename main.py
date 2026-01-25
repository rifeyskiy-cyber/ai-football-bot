import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# ТВОИ КЛЮЧИ
TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка
genai.configure(api_key=AI_KEY)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот ожил! Напиши матч.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        # ЭТОТ СПОСОБ ВЫЗОВА САМЫЙ СТАБИЛЬНЫЙ
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Запрашиваем контент
        response = model.generate_content(f"Ты футбольный аналитик. Дай краткий прогноз на матч: {message.text}")
        
        # Проверяем наличие текста в ответе
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не смог сгенерировать текст. Попробуй другой матч.")
            
    except Exception as e:
        # Если снова будет ошибка, мы увидим её точный текст
        await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    # Очистка очереди перед стартом
    await bot.delete_webhook(drop_pending_updates=True)
    # Даем паузу, чтобы избежать ошибки Conflict
    await asyncio.sleep(5)
    print(">>> БОТ ЗАПУЩЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
