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
    # Используем v1beta и модель 1.5-flash как наиболее стабильную связку
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный аналитик. Проанализируй матч {match_name}. Кто победит и какой вероятный счет? Ответь кратко."
            }]
        }]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_data = await resp.json()
                    return f"❌ Ошибка API: {error_data.get('error', {}).get('message', 'Неизвестная ошибка')}"
        except Exception as e:
            return f"❌ Ошибка сети: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот успешно перезапущен и готов к работе! Напишите матч.")

@dp.message()
async def handle_msg(message: types.Message):
    if not message.text: return
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        logging.error(f"Ошибка в обработчике: {e}")

async def main():
    # ШАГ 1: Разрываем все старые соединения
    print("Принудительная очистка сессий...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    # ШАГ 2: Увеличиваем паузу до 25 секунд
    # Это гарантирует, что старый инстанс на хостинге будет убит по таймауту
    print("Ожидание полной остановки старых копий (25 секунд)...")
    await asyncio.sleep(25) 

    print(">>> БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ <<<")
    try:
        # ШАГ 3: Запускаем с пропуском накопившихся сообщений
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
