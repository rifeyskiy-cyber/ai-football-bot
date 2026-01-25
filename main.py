import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# === ТВОИ ОБНОВЛЕННЫЕ КЛЮЧИ ===
TELEGRAM_TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
GEMINI_API_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"
# ==============================

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("✅ Бот успешно перезапущен с новым токеном! Жду название матча.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        
        prompt = f"Ты футбольный эксперт. Дай краткий прогноз на матч: {message.text}. Кто победит?"
        response = model.generate_content(prompt)
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("⚠️ ИИ задумался, но не дал ответа. Попробуй еще раз.")
            
    except Exception as e:
        # В случае ошибки бот сообщит детали
        logging.error(f"Ошибка: {e}")
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

async def main():
    # 1. Удаляем вебхук, чтобы сбросить старые ошибки Conflict
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print(">>> Вебхук удален, очередь очищена <<<")
    except Exception as e:
        print(f"Ошибка очистки вебхука (не страшно): {e}")

    # 2. Ждем пару секунд, чтобы Telegram принял новое соединение
    await asyncio.sleep(2)

    print(">>> БОТ ЗАПУЩЕН И ГОТОВ <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Критическая ошибка запуска: {e}")
        
