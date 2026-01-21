import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ТВОИ КЛЮЧИ ===
TELEGRAM_TOKEN = "8464793187:AAFqwp0ec_ZOIOd4Jq-AkW-CaiTiDI4PcIo"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
FOOTBALL_API_KEY = "c30951a5dcb846ba9d692fe43e8120c4" # Сохранили на будущее
# ==================

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Инициализация бота БЕЗ прокси (для Koyeb)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ Бот запущен! Я футбольный аналитик на базе Gemini ИИ.\n\nНапиши название матча (например, 'Реал Мадрид - Барселона'), и я дам прогноз!")

@dp.message()
async def handle_message(message: types.Message):
    try:
        # Отправляем статус "печатает", чтобы пользователь видел работу ИИ
        await bot.send_chat_action(message.chat.id, "typing")
        
        prompt = f"Проанализируй футбольный матч и дай подробный прогноз (счет, фаворит, ключевые игроки): {message.text}"
        response = model.generate_content(prompt)
        
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("ИИ не смог сформировать ответ. Попробуй уточнить название матча.")
            
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("⚠️ Произошла ошибка. Проверь правильность API ключей или попробуй позже.")

async def main():
    print(">>> БОТ УСПЕШНО ЗАПУЩЕН НА KOYEB <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
            
