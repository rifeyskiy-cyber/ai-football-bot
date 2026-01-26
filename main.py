import asyncio
import aiohttp
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging

# === ВАШИ КЛЮЧИ ===
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDQsQynmKLfiQCwXyfsqNB45a7ctSwCjyA"
# ===================

# Логирование
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Бот
bot = Bot(token=TOKEN, timeout=60)
dp = Dispatcher()

async def get_gemini_prediction(match_name):
    """Получить прогноз от Gemini AI"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={AI_KEY}"
        
        prompt = f"""Проанализируй футбольный матч {match_name}. 
        Кратко: кто победит, какой счет, почему. 
        Ответь на русском, 3-4 предложения."""
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 200}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    return f"🤖 **AI ПРОГНОЗ:**\n\n{text}\n\n📅 {datetime.now().strftime('%H:%M')}"
    except:
        pass
    
    return None

def get_local_prediction(match_name):
    """Локальный прогноз"""
    match_lower = match_name.lower()
    
    # Популярные матчи
    predictions = {
        'эвертон лидс': ("Эвертон", "2-1", "Домашний стадион и опыт Шона Дайча дадут преимущество."),
        'барселона реал': ("Реал Мадрид", "2-1", "Класс и мотивация Реала перевесят."),
        'реал барселона': ("Реал Мадрид", "3-1", "Атакующая мощь Реала будет ключевой."),
        'арсенал челси': ("Арсенал", "2-0", "Форма Арсенала и проблемы Челси."),
        'манчестер ливерпуль': ("Ливерпуль", "1-2", "Прессинг и скорость Ливерпуля."),
        'ливерпуль манчестер': ("Ливерпуль", "2-0", "Сила на Энфилде."),
        'зенит спартак': ("Зенит", "2-0", "Качество состава Зенита."),
    }
    
    for key, (winner, score, reason) in predictions.items():
        if key in match_lower:
            return f"⚽ **{match_name}**\n\n🏆 **Победитель:** {winner}\n📍 **Счет:** {score}\n💡 **Причина:** {reason}"
    
    # Случайный прогноз для неизвестных матчей
    winner = "Одна из команд"
    score = random.choice(["1-0", "2-1", "1-1", "2-0", "0-0"])
    reasons = [
        "Форма команд будет решающим фактором.",
        "Тактическая подготовка тренеров определит исход.",
        "Мотивация в турнире сыграет ключевую роль.",
        "Ключевые игроки решат судьбу матча."
    ]
    
    return f"⚽ **{match_name}**\n\n🏆 **Победитель:** {winner}\n📍 **Счет:** {score}\n💡 **Анализ:** {random.choice(reasons)}"

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "⚽ **Футбольный аналитик** 🤖\n\n"
        "Отправьте название матча:\n"
        "• Эвертон Лидс\n"
        "• Барселона Реал\n"
        "• Арсенал Челси\n\n"
        "✅ AI активен!",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_message(message: types.Message):
    if not message.text or message.text.startswith('/'):
        return
    
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)
    
    print(f"📥 Запрос: {message.text}")
    
    try:
        # Пробуем Gemini
        ai_prediction = await get_gemini_prediction(message.text)
        
        if ai_prediction:
            response = ai_prediction
            print("✅ Использован AI")
        else:
            response = get_local_prediction(message.text)
            print("✅ Использован локальный прогноз")
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await message.answer(
            f"⚽ **{message.text}**\n\nПрогноз: **{random.choice(['2-1', '1-0'])}**\n"
            f"Вероятный исход: **победа одной из команд**",
            parse_mode="Markdown"
        )

async def cleanup():
    """Простая очистка"""
    print("🔄 Очищаю соединения...")
    
    try:
        # Просто удаляем вебхук
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук удален")
        
        # Ждем
        await asyncio.sleep(3)
        
        # Пробуем получить обновления чтобы сбросить offset
        try:
            updates = await bot.get_updates(limit=1, timeout=1)
            if updates:
                await bot.get_updates(offset=updates[-1].update_id + 1, timeout=1)
                print("✅ Offset сброшен")
        except:
            pass
            
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")

async def main():
    print("=" * 50)
    print("🤖 ЗАПУСК ФУТБОЛЬНОГО БОТА")
    print("=" * 50)
    
    # Очистка
    await cleanup()
    
    print("✅ Бот готов!")
    print("📱 Напишите /start в Telegram")
    print("=" * 50)
    
    # Простой запуск
    try:
        await dp.start_polling(bot, skip_updates=True, polling_timeout=30)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
