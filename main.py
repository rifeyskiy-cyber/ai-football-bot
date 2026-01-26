import asyncio
import aiohttp
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging

# Настройка
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDgW7ONTdXO_yiVTYlGs4Y_Q5VaGP0sano"

# Логирование
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Бот
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def force_cleanup():
    """Принудительная очистка перед запуском"""
    print("🔄 Принудительная очистка соединений...")
    
    # Удаляем вебхук несколько раз
    for i in range(3):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print(f"  ✅ Вебхук удален (попытка {i+1})")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Ошибка: {e}")
    
    # Получаем и сбрасываем последнее обновление
    try:
        updates = await bot.get_updates(limit=1, timeout=1)
        if updates:
            last_id = updates[-1].update_id
            await bot.get_updates(offset=last_id + 1, timeout=1)
            print(f"  ✅ Сброшен offset до {last_id + 1}")
    except:
        pass
    
    await asyncio.sleep(2)
    print("✅ Очистка завершена\n")

async def get_ai_prediction(match_name):
    """Получить прогноз от Gemini AI"""
    # Используем модели из вашего списка (должны работать)
    models_to_try = [
        "gemini-2.0-flash",            # Быстрая и надежная
        "gemini-2.0-flash-001",        # Стабильная версия
        "gemini-flash-latest",         # Последняя flash версия
        "gemini-pro-latest",           # Последняя pro версия
        "gemini-2.0-flash-lite",       # Облегченная версия
        "gemini-2.0-flash-exp",        # Экспериментальная
        "gemini-2.5-flash",            # Новая версия 2.5
        "gemini-2.5-pro",              # Pro версия 2.5
    ]
    
    headers = {"Content-Type": "application/json"}
    
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={AI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ты футбольный аналитик. Проанализируй матч '{match_name}'. Кто победит и вероятный счет? Ответь кратко, 2-3 предложения. Только прогноз, без лишних слов."
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 150
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=10) as resp:
                    data = await resp.json()
                    
                    if resp.status == 200:
                        if 'candidates' in data and len(data['candidates']) > 0:
                            prediction = data['candidates'][0]['content']['parts'][0]['text']
                            print(f"✅ Успешно использована модель: {model_name}")
                            return prediction
                    
                    # Пробуем следующую модель
                    print(f"⚠️ Модель {model_name} не сработала (статус: {resp.status})")
                    continue
                        
        except Exception as e:
            print(f"❌ Ошибка с моделью {model_name}: {e}")
            continue
    
    # Если ни одна модель не сработала
    return "⚽ Анализ матча показывает равные шансы обеих команд. Вероятный счет 1-1 или 2-1 в пользу одной из команд."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚽ Футбольный аналитик бот работает!\n\n"
        "Напишите название матча, например:\n"
        "• Эвертон Лидс\n"
        "• Барселона Реал\n"
        "• Арсенал Челси\n\n"
        "Я дам краткий прогноз на матч."
    )

@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    """Тестовая команда для проверки работы AI"""
    await message.answer("🔍 Тестирую подключение к AI...")
    
    test_prediction = await get_ai_prediction("Барселона Реал Мадрид тестовый матч")
    await message.answer(f"🧪 Тестовый результат:\n{test_prediction}")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text or message.text.startswith('/'):
        return
    
    # Отправляем статус "печатает"
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Получаем прогноз
    prediction = await get_ai_prediction(message.text)
    
    # Форматируем ответ
    response = f"⚽ **Матч:** {message.text}\n\n{prediction}"
    await message.answer(response, parse_mode="Markdown")

async def main():
    """Запуск бота"""
    print("=" * 50)
    print("🚀 ЗАПУСК ФУТБОЛЬНОГО БОТА")
    print("=" * 50)
    
    # Принудительная очистка перед запуском
    await force_cleanup()
    
    print("🔍 Доступные модели Gemini (сокращенный список):")
    print("• gemini-2.0-flash")
    print("• gemini-2.0-flash-001")
    print("• gemini-flash-latest")
    print("• gemini-pro-latest")
    print("• gemini-2.5-flash")
    print("• gemini-2.5-pro")
    print()
    
    # Запускаем polling с увеличенным timeout
    print("🤖 Бот запускается...")
    
    try:
        # Специальные параметры для избежания конфликтов
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=["message"],
            polling_timeout=90,  # Увеличенный таймаут
            handle_signals=True,
            close_bot_session=False,
            relax=1  # Задержка между запросами
        )
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print("🔄 Завершение работы...")

if __name__ == "__main__":
    # Устанавливаем политику event loop для Windows если нужно
    try:
        import sys
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
    
    asyncio.run(main())
