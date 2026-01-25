import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8464793187:AAGJTmJaiO5mHSaEq_D3cs_Owa7IQStk1sc"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_ai_prediction(match_name):
    # Прямой URL к стабильной версии API Gemini
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={AI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Ты футбольный эксперт. Дай краткий прогноз на матч: {match_name}"}]}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"❌ Ошибка Google API: {resp.status}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ Бот запущен! Теперь он работает напрямую через API. Напиши матч.")

@dp.message()
async def handle_msg(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    # ЯДЕРНЫЙ СБРОС: удаляем вебхук и закрываем сессии несколько раз
    for _ in range(3):
        await bot.delete_webhook(drop_pending_updates=True)
        await asyncio.sleep(2)
    
    print(">>> БОТ ВКЛЮЧЕН НАПРЯМУЮ <<<")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
