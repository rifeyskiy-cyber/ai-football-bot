import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# ТВОИ КЛЮЧИ
TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка ИИ
genai.configure(api_key=AI_KEY)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция для автоматического подбора рабочей модели
def get_working_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if 'gemini-1.5-flash' in m.name:
                return m.name
    return 'models/gemini-1.5-flash' # Запасной вариант

WORKING_MODEL_NAME = get_working_model()
model = genai.GenerativeModel(WORKING_MODEL_NAME)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"✅ Бот готов! Использую модель: {WORKING_MODEL_NAME}\nНапиши название матча.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        # Прямой вызов генерации
        response = model.generate_content(f"Дай прогноз на футбол: {message.text}")
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ вернул пустой ответ.")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2)
    print(f">>> ЗАПУСК. МОДЕЛЬ: {WORKING_MODEL_NAME} <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
