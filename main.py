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
    await message.answer("✅ Бот запущен! Напиши матч.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Используем универсальный вызов модели
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Прогноз на футбольный матч: {message.text}")
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не смог сгенерировать текст.")
            
    except Exception as e:
        # Если ошибка 404 — попробуем альтернативное имя модели прямо на лету
        try:
            model = genai.GenerativeModel('models/gemini-pro')
            response = model.generate_content(f"Прогноз на футбол: {message.text}")
            await message.answer(response.text)
        except:
            await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    # ПРИНУДИТЕЛЬНО РАЗРЫВАЕМ ВСЕ СТАРЫЕ СВЯЗИ
    await bot.delete_webhook(drop_pending_updates=True)
    print("Ожидание сброса сессии (10 секунд)...")
    await asyncio.sleep(10) 
    print(">>> БОТ ВКЛЮЧЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
