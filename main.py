import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ТВОИ КЛЮЧИ
TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция прямого запроса к Google без капризных библиотек
async def get_ai_prediction(match_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"Ты футбольный эксперт. Дай краткий прогноз на матч: {match_name}. Кто победит и какой счет?"}]
        }]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            try:
                # Достаем текст из прямого ответа Google
                return data['candidates'][0]['content']['parts'][0]['text']
            except:
                return f"⚠️ Ошибка Google: {data.get('error', {}).get('message', 'Неизвестная ошибка')}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот запущен НАПРЯМУЮ! Теперь всё должно работать. Напиши матч.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    # Сброс всех зависших сессий
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(5)
    print(">>> БОТ ЗАПУЩЕН НАПРЯМУЮ <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
