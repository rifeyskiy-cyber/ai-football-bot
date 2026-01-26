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
    """
    Получает прогноз от Gemini API
    ИСПРАВЛЕНИЕ: Изменен URL API для правильной версии модели
    """
    # ИСПРАВЛЕННЫЙ URL для gemini-1.5-flash
    # Варианты правильных URL:
    
    # Вариант 1 (рекомендуемый): Используем стабильную версию
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={AI_KEY}"
    
    # Вариант 2 (альтернативный): Если первый не работает
    # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={AI_KEY}"
    
    # Вариант 3: Более простая модель
    # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный аналитик. Проанализируй матч {match_name}. Кто победит и вероятный счет? Ответь кратко, максимум 2-3 предложения."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 150  # Ограничиваем длину ответа
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                data = await resp.json()
                
                if resp.status == 200:
                    if 'candidates' in data and len(data['candidates']) > 0:
                        return data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "🤖 Матч проанализирован, но ответ не содержит прогноза."
                
                # Детализированная обработка ошибок
                elif resp.status == 404:
                    return f"❌ Ошибка: Модель не найдена. Возможно, неверное название модели в URL."
                elif resp.status == 400:
                    error_msg = data.get('error', {}).get('message', 'Неизвестная ошибка')
                    return f"❌ Ошибка запроса: {error_msg}"
                else:
                    return f"❌ Ошибка API (код {resp.status}): {data}"
                    
        except aiohttp.ClientTimeout:
            return "⏱️ Таймаут запроса к AI. Попробуйте позже."
        except aiohttp.ClientError as e:
            return f"🌐 Ошибка сети: {str(e)}"
        except Exception as e:
            logging.error(f"Ошибка в get_ai_prediction: {e}")
            return f"⚠️ Внутренняя ошибка: {str(e)}"

# Инициализация бота с кастомной сессией
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"⚽️ Футбольный аналитик бот запущен! (Сессия: {session_id})\n\n"
        "Напиши название футбольного матча в формате:\n"
        "• 'Барселона Реал Мадрид'\n"
        "• 'Манчестер Юнайтед Ливерпуль'\n"
        "• 'Зенит Спартак'\n\n"
        "Я проанализирую и дам прогноз на матч!"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📋 Помощь по боту:\n\n"
        "Просто напишите название матча, например:\n"
        "• Арсенал Челси\n"
        "• Бавария Боруссия\n"
        "• Россия Испания\n\n"
        "Я дам краткий анализ и вероятный счет.\n\n"
        "/start - Перезапустить бота\n"
        "/help - Эта справка\n"
        "/info - Информация о боте"
    )

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer(
        f"📊 Информация о боте:\n"
        f"• ID сессии: {session_id}\n"
        f"• Модель AI: Gemini 1.5 Flash\n"
        f"• Статус: Активен ✅\n"
        f"• Для анализа используйте названия команд или стран"
    )

@dp.message()
async def handle_msg(message: types.Message):
    if not message.text or message.text.startswith('/'):
        return
    
    # Убираем лишние пробелы
    match_name = ' '.join(message.text.split()).strip()
    
    if not match_name or len(match_name) < 3:
        await message.answer("⚠️ Пожалуйста, введите название матча (например: 'Барселона Реал')")
        return
    
    # Показываем статус "печатает"
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        prediction = await get_ai_prediction(match_name)
        # Форматируем ответ
        formatted_response = f"⚽ **Матч:** {match_name}\n\n{prediction}\n\n📅 *Прогноз сгенерирован AI*"
        await message.answer(formatted_response, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in handle_msg: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса. Попробуйте еще раз.")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print(f"--- ЗАПУСК СЕССИИ {session_id} ---")
    
    # ПРИНУДИТЕЛЬНЫЙ РАЗРЫВ: устанавливаем и тут же удаляем вебхук
    try:
        await bot.set_webhook(url=f"https://example.com/{session_id}", drop_pending_updates=True)
        await asyncio.sleep(1)
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Старые соединения принудительно разорваны.")
    except Exception as e:
        print(f"⚠️ Ошибка при очистке вебхука: {e}")
    
    # Даем Telegram время на смену режима
    await asyncio.sleep(2)
    
    print(f">>> БОТ {session_id} ГОТОВ <<<")
    print("Ожидание сообщений...")
    
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        if bot.session:
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n⏹️ Бот {session_id} остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
