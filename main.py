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
    # Используем v1beta и модель 1.5-flash против ошибок 404 и лимитов
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный аналитик. Дай краткий прогноз на матч: {match_name}. Кто победит и какой вероятный счет?"
            }]
        }]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=15) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_msg = data.get('error', {}).get('message', 'Ошибка API')
                    return f"❌ Ошибка Google: {error_msg}"
        except Exception as e:
            return f"❌ Ошибка сети: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот запущен и готов к прогнозам! Просто напиши название матча.")

@dp.message()
async def handle_msg(message: types.Message):
    if not message.text: return
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def main():
    print("Уничтожение старых сессий...")
    # Очищаем вебхуки
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Ждем, пока облако завершит старые процессы, чтобы избежать ConflictError
    print("Ожидание стабилизации (15 секунд)...")
    await asyncio.sleep(15) 

    print(">>> БОТ ЗАПУЩЕН НАПРЯМУЮ <<<")
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
        
