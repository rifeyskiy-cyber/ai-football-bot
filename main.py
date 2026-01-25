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

# Мы используем это имя модели без лишних префиксов, 
# библиотека сама подставит нужную версию API
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("✅ Бот готов! Напиши матч, и я дам прогноз.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Основной запрос к ИИ
        response = model.generate_content(f"Ты футбольный аналитик. Дай прогноз на матч: {message.text}")
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не смог сгенерировать текст ответа.")
            
    except Exception as e:
        # Если снова будет 404, мы увидим это, но этот код должен решить проблему
        await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    # Очищаем старые сообщения перед стартом
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2)
    print(">>> БОТ ВКЛЮЧЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
