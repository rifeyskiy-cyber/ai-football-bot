import asyncio
import aiohttp
import random
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging

# === ВАШИ КЛЮЧИ ===
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDQsQynmKLfiQCwXyfsqNB45a7ctSwCjyA"  # Ваш новый ключ
# ===================

# Логирование
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Бот
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def test_gemini_connection():
    """Проверка подключения к Gemini API с новым ключом"""
    print("🔍 Проверяю подключение к Gemini API...")
    
    # Пробуем разные модели (ваши доступные)
    models_to_try = [
        "gemini-2.0-flash-exp",  # Экспериментальная (часто работает)
        "gemini-2.0-flash",      # Стандартная
        "gemini-2.0-flash-001",  # Стабильная версия
        "gemini-flash-latest",   # Последняя
        "gemini-pro-latest",     # Pro версия
    ]
    
    working_model = None
    
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={AI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": "Привет! Работаешь?"}]
            }],
            "generationConfig": {
                "maxOutputTokens": 10
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        print(f"✅ Модель '{model}' работает!")
                        working_model = model
                        break
                    else:
                        error_data = await resp.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown')
                        print(f"❌ Модель '{model}': {error_msg[:60]}")
        except Exception as e:
            print(f"⚠️ Модель '{model}': {str(e)[:50]}")
    
    return working_model

async def get_gemini_prediction(match_name):
    """Получить прогноз от Gemini AI"""
    # Находим работающую модель
    model = await test_gemini_connection()
    
    if not model:
        return None  # Gemini не работает
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={AI_KEY}"
    
    # Улучшенный промпт для футбольного анализа
    prompt = f"""Ты опытный футбольный аналитик и букмекер. Проанализируй матч: {match_name}

Дай детальный прогноз в следующем формате:

1. **Вероятный победитель**: [Название команды]
2. **Предполагаемый счет**: [Счет, например 2-1]
3. **Ключевые факторы**: [2-3 фактора, которые решат матч]
4. **Рекомендация по ставке**: [Краткая рекомендация]

Анализ должен быть:
- Кратким (4-5 предложений)
- Конкретным
- На русском языке
- Без лишних слов

Пример ответа:
1. **Вероятный победитель**: Барселона
2. **Предполагаемый счет**: 2-1
3. **Ключевые факторы**: Контроль мяча Барселоны, уязвимость защиты Реала на контратаках
4. **Рекомендация по ставке**: Победа Барселоны с учетом формы команд"""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": 400
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        prediction = data['candidates'][0]['content']['parts'][0]['text']
                        print(f"✅ Получен прогноз от Gemini ({model})")
                        return prediction
                else:
                    print(f"❌ Ошибка Gemini API: {resp.status}")
                    return None
    except Exception as e:
        print(f"⚠️ Ошибка при запросе: {e}")
        return None

def generate_local_prediction(match_name):
    """Локальный прогноз (запасной вариант)"""
    # Простая база команд
    teams_db = {
        'эвертон': {'сила': 75, 'тренер': 'Шон Дайч', 'форма': 'средняя'},
        'лидс': {'сила': 70, 'тренер': 'Даниэль Фарке', 'форма': 'нестабильная'},
        'барселона': {'сила': 94, 'тренер': 'Хави', 'форма': 'хорошая'},
        'реал': {'сила': 96, 'тренер': 'Анчелотти', 'форма': 'отличная'},
        'реал мадрид': {'сила': 96, 'тренер': 'Анчелотти', 'форма': 'отличная'},
        'манчестер юнайтед': {'сила': 82, 'тренер': 'тен Хаг', 'форма': 'неубедительная'},
        'ливерпуль': {'сила': 93, 'тренер': 'Клопп', 'форма': 'хорошая'},
        'арсенал': {'сила': 92, 'тренер': 'Артета', 'форма': 'отличная'},
        'манчестер сити': {'сила': 95, 'тренер': 'Гвардиола', 'форма': 'отличная'},
        'челси': {'сила': 85, 'тренер': 'Почеттино', 'форма': 'слабая'},
        'зенит': {'сила': 88, 'тренер': 'Семак', 'форма': 'хорошая'},
        'спартак': {'сила': 85, 'тренер': 'Абаскаль', 'форма': 'нестабильная'},
    }
    
    # Извлекаем команды
    words = match_name.lower().split()
    team1 = team2 = None
    
    # Ищем команды в базе
    for i in range(len(words)):
        for j in range(i+1, len(words)+1):
            phrase = ' '.join(words[i:j])
            if phrase in teams_db:
                if not team1:
                    team1 = phrase
                elif not team2:
                    team2 = phrase
                    break
        if team1 and team2:
            break
    
    if not team1 or not team2:
        # Если не нашли, используем первые слова
        team1 = words[0] if len(words) > 0 else "Команда А"
        team2 = words[1] if len(words) > 1 else "Команда Б"
        team1_data = {'сила': random.randint(70, 90), 'тренер': 'Неизвестно', 'форма': 'средняя'}
        team2_data = {'сила': random.randint(70, 90), 'тренер': 'Неизвестно', 'форма': 'средняя'}
    else:
        team1_data = teams_db.get(team1, {'сила': 75, 'тренер': 'Неизвестно', 'форма': 'средняя'})
        team2_data = teams_db.get(team2, {'сила': 75, 'тренер': 'Неизвестно', 'форма': 'средняя'})
    
    # Рассчитываем
    total = team1_data['сила'] + team2_data['сила']
    prob1 = team1_data['сила'] / total * 100
    prob2 = team2_data['сила'] / total * 100
    
    # Определяем победителя
    if prob1 > prob2:
        winner = team1.title()
        winner_prob = prob1
        loser = team2.title()
    else:
        winner = team2.title()
        winner_prob = prob2
        loser = team1.title()
    
    # Генерируем счет
    diff = abs(team1_data['сила'] - team2_data['сила'])
    if diff > 20:
        if team1_data['сила'] > team2_data['сила']:
            score = f"{random.randint(2,3)}-{random.randint(0,1)}"
        else:
            score = f"{random.randint(0,1)}-{random.randint(2,3)}"
    elif diff > 10:
        if team1_data['сила'] > team2_data['сила']:
            score = f"{random.randint(1,2)}-{random.randint(0,1)}"
        else:
            score = f"{random.randint(0,1)}-{random.randint(1,2)}"
    else:
        score = f"{random.randint(0,2)}-{random.randint(0,2)}"
    
    # Формируем прогноз
    factors = [
        "Текущая форма команд",
        "Травмы ключевых игроков",
        "Мотивация в турнире",
        "Тактические схемы тренеров",
        "История личных встреч"
    ]
    
    prediction = (
        f"⚽ **МАТЧ:** {match_name}\n\n"
        f"🎯 **ПРОГНОЗ:**\n"
        f"• Вероятный победитель: **{winner}** ({winner_prob:.1f}%)\n"
        f"• Предполагаемый счет: **{score}**\n"
        f"• Тренеры: {team1_data['тренер']} vs {team2_data['тренер']}\n\n"
        f"🔑 **КЛЮЧЕВЫЕ ФАКТОРЫ:**\n"
        f"• {random.choice(factors)}\n"
        f"• {random.choice(factors)}\n\n"
        f"📊 *Локальный анализ | {datetime.now().strftime('%H:%M')}*"
    )
    
    return prediction

async def get_football_prediction(match_name):
    """Основная функция получения прогноза"""
    print(f"\n📥 Анализирую матч: '{match_name}'")
    
    # 1. Пробуем Gemini API
    gemini_prediction = await get_gemini_prediction(match_name)
    
    if gemini_prediction:
        # Форматируем ответ Gemini
        response = f"🤖 **GEMINI AI ПРОГНОЗ | {match_name}**\n\n{gemini_prediction}\n\n"
        response += f"📅 *Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}*"
        return response
    
    # 2. Если Gemini не сработал, используем локальный
    print("⚠️ Gemini не ответил, использую локальный анализ")
    return generate_local_prediction(match_name)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚽ **УМНЫЙ ФУТБОЛЬНЫЙ АНАЛИТИК** 🤖\n\n"
        "Я анализирую матчи с помощью искусственного интеллекта Gemini!\n\n"
        "📝 *Как использовать:*\n"
        "Просто напишите название матча:\n"
        "• `Эвертон Лидс`\n"
        "• `Барселона Реал Мадрид`\n"
        "• `Манчестер Юнайтед Ливерпуль`\n"
        "• `Зенит Спартак`\n\n"
        "⚡ *Возможности:*\n"
        "• AI-анализ от Google Gemini\n"
        "• Прогноз победителя и счета\n"
        "• Ключевые факторы матча\n"
        "• Рекомендации по ставкам\n\n"
        "🔧 *Команды:*\n"
        "`/start` - это сообщение\n"
        "`/test` - проверить AI\n"
        "`/help` - помощь\n"
        "`/status` - статус бота",
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "📋 **ПОМОЩЬ ПО БОТУ:**\n\n"
        "1. Напишите название матча в формате:\n"
        "   `Команда1 Команда2`\n\n"
        "2. Примеры:\n"
        "   • `Эвертон Лидс`\n"
        "   • `Реал Мадрид Барселона`\n"
        "   • `Арсенал Челси`\n\n"
        "3. Бот использует:\n"
        "   • **Gemini AI** от Google (основной)\n"
        "   • Локальный анализ (запасной)\n\n"
        "4. Если есть проблемы:\n"
        "   • Проверьте написание команд\n"
        "   • Используйте полные названия\n"
        "   • Подождите 5-10 секунд ответа",
        parse_mode="Markdown"
    )

@dp.message(Command("test"))
async def test_cmd(message: types.Message):
    """Тест работы AI"""
    await message.answer("🧪 Тестирую подключение к Gemini AI...")
    
    model = await test_gemini_connection()
    
    if model:
        # Тестовый запрос
        test_match = "Барселона Реал Мадрид (тест)"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={AI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Краткий прогноз на матч {test_match}. Ответь 'Тест пройден'."}]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        await message.answer(f"✅ **GEMINI AI РАБОТАЕТ!**\nМодель: `{model}`")
                    else:
                        await message.answer("⚠️ Gemini отвечает с ошибкой")
        except:
            await message.answer("❌ Ошибка подключения к Gemini")
    else:
        await message.answer("❌ Нет работающих моделей Gemini\n🤖 Используется локальный режим")

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    """Статус бота"""
    model = await test_gemini_connection()
    
    status_text = (
        f"📊 **СТАТУС БОТА:**\n\n"
        f"• 🤖 Режим: {'**Gemini AI** ✅' if model else '**Локальный** ⚠️'}\n"
        f"• ⏰ Время: {datetime.now().strftime('%H:%M:%S')}\n"
        f"• 📅 Дата: {datetime.now().strftime('%d.%m.%Y')}\n"
        f"• 🎯 Модель: `{model if model else 'Локальный анализ'}`\n"
        f"• 🔄 Ключ: {'Активен' if model else 'Проблема'}\n\n"
        f"💡 *Рекомендация:* {'Отправьте матч для AI-анализа!' if model else 'Используйте полные названия команд'}"
    )
    
    await message.answer(status_text, parse_mode="Markdown")

@dp.message()
async def handle_message(message: types.Message):
    """Обработка всех сообщений"""
    if not message.text or message.text.startswith('/'):
        return
    
    # Показываем "печатает..."
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Небольшая задержка для реалистичности
    await asyncio.sleep(1)
    
    try:
        # Получаем прогноз
        prediction = await get_football_prediction(message.text)
        
        # Отправляем ответ
        await message.answer(prediction, parse_mode="Markdown")
        
        print(f"✅ Прогноз отправлен для '{message.text}'")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        # Аварийный ответ
        await message.answer(
            f"⚽ **МАТЧ:** {message.text}\n\n"
            f"⚠️ *Произошла ошибка анализа*\n"
            f"Попробуйте:\n"
            f"1. Проверить написание команд\n"
            f"2. Использовать пример: `Эвертон Лидс`\n"
            f"3. Подождать минуту и повторить\n\n"
            f"🔄 *Бот переключен в локальный режим*",
            parse_mode="Markdown"
        )

async def main():
    """Запуск бота"""
    print("=" * 60)
    print("🤖 ЗАПУСК ФУТБОЛЬНОГО АНАЛИТИКА С GEMINI AI")
    print("=" * 60)
    
    # Тестируем ключ при запуске
    print(f"\n🔑 Ваш ключ Gemini: {AI_KEY[:10]}...{AI_KEY[-5:]}")
    model = await test_gemini_connection()
    
    if model:
        print(f"✅ Gemini AI активен! Модель: {model}")
    else:
        print("⚠️ Gemini недоступен, используется локальный режим")
    
    # Очистка вебхука
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("\n✅ Бот готов к работе!")
    print("📱 Отправьте /start в Telegram")
    print("=" * 60)
    
    # Запуск polling
    try:
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=["message"],
            polling_timeout=30,
            relax=0.1
        )
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
