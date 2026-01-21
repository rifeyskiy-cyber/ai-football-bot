import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# Твои ключи
TELEGRAM_TOKEN = "8464793187:AAFqwp0ec_ZOIOd4Jq-AkW-CaiTiDI4PcIo"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

# Настройка ИИ с ПРАВИЛЬНЫМ именем модели
genai.configure(api_key=GEMINI_API_KEY)
# Попробуем БЕЗ приставки models/ если не работало с ней, или С ней. 
# Самый надежный вариант сейчас:
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("🤖 Бот ожил! Я тебя слышу. Напиши название матча.")

@dp.message()
async def handle_message(message: types.Message):
    print(f"Получено сообщение: {message.text}") # Это появится в логах Koyeb
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = f"Дай краткий футбольный прогноз на матч: {message.text}"
        response = model.generate_content(prompt)
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("ИИ прислал пустой ответ.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        # Бот напишет тебе в чат, какая именно ошибка произошла!
        await message.answer(f"⚠️ Ошибка ИИ: {str(e)}")

async def main():
    # ГАРАНТИРОВАННО СБРАСЫВАЕМ ВСЕ СТАРЫЕ СВЯЗИ
    await bot.delete_webhook(drop_pending_updates=True)
    print(">>> СВЯЗЬ С TELEGRAM УСТАНОВЛЕНА <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
