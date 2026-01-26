import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# КЛЮЧИ
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDgW7ONTdXO_yiVTYlGs4Y_Q5VaGP0sano"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_ai_prediction(match_name):
    # Самый надежный эндпоинт для 1.5-flash
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот успешно перезапущен! Напиши матч.")

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
    print("--- ЗАПУСК СИСТЕМЫ ОЧИСТКИ ---")
    
    # 1. Мгновенный разрыв старых соединений через установку пустого вебхука
    await bot.set_webhook(url='https://google.com', drop_pending_updates=True)
    await asyncio.sleep(1)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 2. Техническая пауза для сброса состояния на серверах Telegram
    print("Ожидание стабилизации (10 секунд)...")
    await asyncio.sleep(10) 

    print(">>> БОТ АКТИВИРОВАН И ГОТОВ <<<")
    try:
        # 3. Запуск основного цикла
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
