import logging
import asyncio
import aiohttp
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# КЛЮЧИ
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDgW7ONTdXO_yiVTYlGs4Y_Q5VaGP0sano"

# Создаем уникальный ID для текущего запуска бота
session_id = str(uuid.uuid4())[:8]

async def get_ai_prediction(match_name):
    """Получает прогноз от Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный аналитик. Проанализируй матч {match_name}. Кто победит и вероятный счет? Ответь кратко, максимум 2-3 предложения."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 150
        }
    }

    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                data = await resp.json()
                
                if resp.status == 200:
                    if 'candidates' in data and len(data['candidates']) > 0:
                        return data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "🤖 Матч проанализирован, но ответ не содержит прогноза."
                else:
                    error_msg = data.get('error', {}).get('message', 'Неизвестная ошибка')
                    return f"❌ Ошибка API: {error_msg}"
                    
        except aiohttp.ClientTimeout:
            return "⏱️ Таймаут запроса к AI. Попробуйте позже."
        except Exception as e:
            logging.error(f"Ошибка в get_ai_prediction: {e}")
            return f"⚠️ Ошибка: {str(e)}"

# Инициализация бота
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
        "📋 Просто напишите название матча!\n"
        "Например: 'Арсенал Челси' или 'Бразилия Аргентина'"
    )

@dp.message()
async def handle_msg(message: types.Message):
    if not message.text or message.text.startswith('/'):
        return
    
    match_name = ' '.join(message.text.split()).strip()
    
    if not match_name or len(match_name) < 3:
        await message.answer("⚠️ Пожалуйста, введите название матча (например: 'Барселона Реал')")
        return
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        prediction = await get_ai_prediction(match_name)
        response = f"⚽ **Матч:** {match_name}\n\n{prediction}\n\n📅 *Прогноз сгенерирован AI*"
        await message.answer(response, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in handle_msg: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте еще раз.")

async def main():
    """Основная функция запуска бота"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print(f"\n{'='*50}")
    print(f"🚀 ЗАПУСК ФУТБОЛЬНОГО БОТА")
    print(f"📱 Session ID: {session_id}")
    print(f"{'='*50}\n")
    
    # Очистка перед запуском
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук удален")
        await asyncio.sleep(2)
    except Exception as e:
        print(f"⚠️ Ошибка при очистке: {e}")
    
    print("🔄 Бот запускается...")
    
    try:
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем правильный метод запуска
        print("📡 Начинаю прослушивание сообщений...")
        
        # Запускаем polling с явными параметрами
        await dp.start_polling(
            bot,
            skip_updates=True,  # Пропускаем старые сообщения
            allowed_updates=["message", "callback_query"],  # Какие типы обновлений слушаем
            polling_timeout=30,  # Таймаут для запросов
            handle_signals=True  # Обработка сигналов (Ctrl+C)
        )
        
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен по запросу пользователя")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        print("🔄 Завершение работы...")
        try:
            await bot.session.close()
            print("✅ Сессия закрыта")
        except:
            pass

if __name__ == "__main__":
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Создаем event loop и запускаем бота
    try:
        # Для Windows может потребоваться эта настройка
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        # Запускаем основную функцию
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
