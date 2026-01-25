import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# ТВОИ РАБОЧИЕ КЛЮЧИ
TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка ИИ
genai.configure(api_key=AI_KEY)

# МЫ МЕНЯЕМ МОДЕЛЬ НА ТУ, КОТОРАЯ ТОЧНО ЕСТЬ В СТАБИЛЬНОЙ ВЕРСИИ
# Это исправит ошибку 404
model = genai.GenerativeModel('gemini-1.5-flash-latest')

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ ПОБЕДА! Бот полностью готов. Напиши название матча.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Генерируем ответ
        response = model.generate_content(f"Ты футбольный аналитик. Дай прогноз на матч: {message.text}")
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не смог сформулировать ответ.")
            
    except Exception as e:
        # Если вдруг снова будет ошибка, мы увидим её текст
        await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    # Очистка очереди перед стартом
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2)
    print(">>> БОТ ВКЛЮЧЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
