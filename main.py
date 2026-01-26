import logging
import asyncio
import aiohttp
import uuid  # Для создания уникального ID сессии
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

# КЛЮЧИ
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDgW7ONTdXO_yiVTYlGs4Y_Q5VaGP0sano"

# Создаем уникальный ID для текущего запуска бота
session_id = str(uuid.uuid4())[:8]

async def get_ai_prediction(match_name):
    # Стабильный эндпоинт для gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": f"Ты футбольный аналитик. Проанализируй матч {match_name}. Кто победит и вероятный счет? Ответь кратко."}]}]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=15) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                return f"❌ Ошибка API: {data.get('error', {}).get('message', 'Неизвестная ошибка')}"
        except Exception as e:
            return f"❌ Ошибка сети: {str(e)}"

# Инициализация бота с кастомной сессией
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"⚽️ Бот запущен! (Session: {session_id})\nНапиши название матча.")

@dp.message()
async def handle_msg(message: types.Message):
    if not message.text: return
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        logging.error(f"Error: {e}")

async def main():
    print(f"--- ЗАПУСК СЕССИИ {session_id} ---")
    
    # ПРИНУДИТЕЛЬНЫЙ РАЗРЫВ: устанавливаем и тут же удаляем вебхук
    # Это мощнее, чем просто delete_webhook
    try:
        await bot.set_webhook(url=f"https://example.com/{session_id}", drop_pending_updates=True)
        await asyncio.sleep(2)
        await bot.delete_webhook(drop_pending_updates=True)
        print("Старые соединения принудительно разорваны.")
    except Exception as e:
        print(f"Ошибка при очистке: {e}")
    
    # Даем Telegram 5 секунд на осознание смены режима
    await asyncio.sleep(5) 

    print(f">>> БОТ {session_id} ГОТОВ <<<")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
