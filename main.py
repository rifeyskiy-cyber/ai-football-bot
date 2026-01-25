import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ТВОИ КЛЮЧИ (сохранены из оригинала)
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyAAXH0yNGu3l1fae7p5hXNLpASW2ydt1Ns"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_ai_prediction(match_name):
    # Используем v1beta и gemini-2.0-flash для исключения ошибки 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный аналитик. Проанализируй матч {match_name}. Напиши вероятный исход и счет. Отвечай кратко и профессионально."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 400
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=15) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_msg = data.get('error', {}).get('message', 'Неизвестная ошибка')
                    # Если всё же 404, пробуем подсказать причину
                    if resp.status == 404:
                        return "❌ Ошибка 404: Модель не найдена. Проверьте регион API или название модели (gemini-2.0-flash)."
                    return f"❌ Ошибка Google (Status {resp.status}): {error_msg}"
        except Exception as e:
            return f"❌ Ошибка сети: {str(e)}"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("⚽️ **Футбольный AI-Бот запущен!**\nНапиши название матча (например: Реал Мадрид - Барселона), и я дам прогноз.")

@dp.message()
async def handle_msg(message: types.Message):
    if not message.text:
        return
        
    try:
        # Индикация того, что бот "думает"
        await bot.send_chat_action(message.chat.id, "typing")
        prediction = await get_ai_prediction(message.text)
        await message.answer(prediction)
    except Exception as e:
        logging.error(f"Ошибка в handle_msg: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке запроса.")

async def main():
    # 1. Очистка старых сессий для устранения TelegramConflictError
    [span_5](start_span)[span_6](start_span)print("Уничтожение старых сессий...")[span_5](end_span)[span_6](end_span)
    [span_7](start_span)await bot.delete_webhook(drop_pending_updates=True)[span_7](end_span)
    
    # Небольшая пауза, чтобы Telegram успел закрыть предыдущее соединение
    await asyncio.sleep(2) 

    [span_8](start_span)[span_9](start_span)print(">>> БОТ ЗАПУЩЕН НАПРЯМУЮ <<<")[span_8](end_span)[span_9](end_span)
    
    try:
        # 2. Запуск polling с пропуском старых сообщений
        [span_10](start_span)await dp.start_polling(bot, skip_updates=True)[span_10](end_span)
    finally:
        # Корректное закрытие сессии при выключении
        await bot.session.close()

if __name__ == "__main__":
    # Настройка логирования для отслеживания SIGTERM в логах
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        [span_11](start_span)[span_12](start_span)print("Бот остановлен пользователем.")[span_11](end_span)[span_12](end_span)
            
