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
    # Пытаемся сначала через v1beta, если не выйдет — через v1
    base_url = "https://generativelanguage.googleapis.com"
    model_path = "/models/gemini-1.5-flash:generateContent"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный аналитик. Проанализируй матч {match_name}. Кто победит и какой вероятный счет? Ответь кратко."
            }]
        }]
    }

    async with aiohttp.ClientSession() as session:
        # Проверка v1beta
        try:
            async with session.post(f"{base_url}/v1beta{model_path}?key={AI_KEY}", json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                
                # Если 404, пробуем стабильный v1
                if resp.status == 404:
                    async with session.post(f"{base_url}/v1{model_path}?key={AI_KEY}", json=payload) as v1_resp:
                        if v1_resp.status == 200:
                            data = await v1_resp.json()
                            return data['candidates'][0]['content']['parts'][0]['text']
                
                error_data = await resp.json()
                return f"❌ Ошибка API ({resp.status}): {error_data.get('error', {}).get('message', 'Unknown error')}"
        except Exception as e:
            return f"❌ Ошибка сети: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот работает! Напиши матч для прогноза.")

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
    # Решение TelegramConflictError
    print("Уничтожение старых сессий...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Ожидание стабилизации системы (15 секунд)...")
    await asyncio.sleep(15) 

    print(">>> БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ <<<")
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
        
