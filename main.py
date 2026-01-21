import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ТВОИ КЛЮЧИ (ПРОВЕРЬ ИХ ТЩАТЕЛЬНО) ===
TELEGRAM_TOKEN = "8464793187:AAElLO8K5Y8zG5SDs2TYqOYfkFrhuupzy6o"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
# ========================================

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ Бот запущен! Напиши матч, и я дам прогноз.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = f"Дай краткий футбольный прогноз на матч: {message.text}"
        response = model.generate_content(prompt)
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("ИИ не смог сформировать ответ.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(f"⚠️ Ошибка: {str(e)}")

async def main():
    # Эта строка решает проблему Conflict и Unauthorized при перезапуске
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Ошибка при удалении вебхука: {e}")
        
    print(">>> БОТ ВКЛЮЧЕН <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
