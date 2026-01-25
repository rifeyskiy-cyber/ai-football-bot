import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ТВОИ КЛЮЧИ ===
TELEGRAM_TOKEN = "8464793187:AAHqvRHl9u_cFxyMPzPMCyvb_hDNgvQ-AIcY"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
# ==================

genai.configure(api_key=GEMINI_API_KEY)
# Используем максимально простую инициализацию модели
model = genai.GenerativeModel('models/gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ БОТ ОЖИЛ! Напиши матч.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = f"Дай краткий прогноз на матч: {message.text}"
        response = model.generate_content(prompt)
        
        # Если ИИ ответил, отправляем текст. Если нет - пишем об этом.
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ получил запрос, но не смог сформулировать текст.")
            
    except Exception as e:
        # Если случится любая ошибка, бот ПРИШЛЕТ её тебе в Telegram!
        await message.answer(f"❌ Ошибка ИИ: {str(e)}")

async def main():
    # ОЧЕНЬ ВАЖНО: Удаляем вебхук перед запуском
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> БОТ ЗАПУЩЕН С ЧИСТОГО ЛИСТА <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
        
