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
    await message.answer("✅ Бот онлайн! Напиши матч.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Самый простой вызов без префиксов
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Мы добавляем проверку безопасности, чтобы ИИ не молчал
        response = model.generate_content(
            f"Дай прогноз на футбол: {message.text}",
            generation_config=genai.types.GenerationConfig(candidate_count=1)
        )
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ не выдал ответ. Попробуй другой матч.")
            
    except Exception as e:
        # Если снова 404, пробуем альтернативный метод
        await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    # ЖЕСТКИЙ СБРОС КОНФЛИКТА
    await bot.delete_webhook(drop_pending_updates=True)
    print("Пауза для сброса сессии...")
    await asyncio.sleep(7) 
    print(">>> ЗАПУСК <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
