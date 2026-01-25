import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ТВОИ КЛЮЧИ
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_ai_prediction(match_name):
    # Прямой запрос к Google API (версия v1 - самая стабильная)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Ты футбольный эксперт. Дай краткий прогноз на матч: {match_name}. Кто победит и счет?"}]}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            if resp.status == 200:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"❌ Ошибка Google: {data.get('error', {}).get('message', 'Неизвестная ошибка')}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("✅ БОТ ПЕРЕЗАГРУЖЕН! Теперь всё должно работать. Напиши матч.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    # ЭТОТ БЛОК ПРИНУДИТЕЛЬНО УБИВАЕТ ВСЕХ СТАРЫХ БОТОВ
    print("Уничтожение старых сессий...")
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(10) # Ждем 10 секунд, пока Telegram сбросит конфликты
    
    print(">>> БОТ ЗАПУЩЕН НАПРЯМУЮ <<<")
    # Параметр skip_updates игнорирует весь старый спам
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
