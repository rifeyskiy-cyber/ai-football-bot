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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Бот
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_available_models():
    """Получить список доступных моделей"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={AI_KEY}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                models = data.get('models', [])
                print("\n📋 ДОСТУПНЫЕ МОДЕЛИ Gemini:")
                for model in models:
                    if 'generateContent' in model.get('supportedGenerationMethods', []):
                        print(f"• {model['name']} (поддерживает generateContent)")
                return models
            else:
                print(f"❌ Не удалось получить список моделей: {resp.status}")
                return []

async def get_ai_prediction(match_name):
    """Получить прогноз от Gemini AI"""
    # Пробуем разные модели в порядке приоритета
    models_to_try = [
        "gemini-1.5-pro-latest",     # Самая мощная
        "gemini-1.0-pro-latest",     # Стандартная
        "gemini-1.0-pro",           # Базовая
        "gemini-1.5-flash-001",     # Быстрая
        "gemini-1.0-ultra-latest"   # Премиум
    ]
    
    headers = {"Content-Type": "application/json"}
    
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={AI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ты футбольный аналитик. Проанализируй матч '{match_name}'. Кто победит и вероятный счет? Ответь кратко, 2-3 предложения."
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
                            logger.info(f"✅ Успешно использована модель: {model_name}")
                            return prediction
                    
                    # Если ошибка 404, пробуем следующую модель
                    if resp.status == 404:
                        logger.warning(f"Модель {model_name} не найдена, пробую следующую...")
                        continue
                        
        except Exception as e:
            logger.error(f"Ошибка с моделью {model_name}: {e}")
            continue
    
    # Если ни одна модель не сработала
    return "🤖 Не удалось получить прогноз. Возможно, проблема с доступом к API или все модели недоступны."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚽ Футбольный аналитик бот готов!\n\n"
        "Напишите название матча, например:\n"
        "• Эвертон Лидс\n"
        "• Барселона Реал\n"
        "• Арсенал Челси\n\n"
        "Я дам краткий прогноз на матч."
    )

@dp.message(Command("models"))
async def models_cmd(message: types.Message):
    """Команда для проверки доступных моделей"""
    await message.answer("🔄 Проверяю доступные модели Gemini...")
    
    models = await get_available_models()
    if models:
        supported_models = []
        for model in models:
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                model_name = model['name'].split('/')[-1]
                supported_models.append(model_name)
        
        if supported_models:
            response = "📋 Доступные модели:\n" + "\n".join([f"• {model}" for model in supported_models[:10]])
            await message.answer(response)
        else:
            await message.answer("❌ Нет моделей с поддержкой generateContent")
    else:
        await message.answer("❌ Не удалось получить список моделей")

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
    
    # Проверяем доступные модели при запуске
    print("\n🔍 Проверяю доступные модели Gemini API...")
    await get_available_models()
    
    # Удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Бот готов к работе")
    print("📱 Отправьте /start в Telegram")
    
    # Запускаем polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
