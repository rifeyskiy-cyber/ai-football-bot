import asyncio
import aiohttp
import random
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
import os
import signal
import sys

# === ВАШИ КЛЮЧИ ===
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDQsQynmKLfiQCwXyfsqNB45a7ctSwCjyA"
# ===================

# Создаем уникальный ID для этого экземпляра
import uuid
INSTANCE_ID = str(uuid.uuid4())[:8]

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s - {INSTANCE_ID} - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class FootballBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN, timeout=90)
        self.dp = Dispatcher()
        self.setup_handlers()
        print(f"\n{'='*60}")
        print(f"🤖 ФУТБОЛЬНЫЙ БОТ (Экземпляр: {INSTANCE_ID})")
        print(f"{'='*60}")
    
    def setup_handlers(self):
        @self.dp.message(Command("start"))
        async def start_cmd(message: types.Message):
            await message.answer(
                f"⚽ **ФУТБОЛЬНЫЙ АНАЛИТИК** 🤖\n"
                f"ID экземпляра: `{INSTANCE_ID}`\n\n"
                "📝 *Отправьте матч:*\n"
                "`Эвертон Лидс`\n"
                "`Барселона Реал`\n"
                "`Арсенал Челси`\n\n"
                "✅ *Gemini AI активен!*",
                parse_mode="Markdown"
            )
        
        @self.dp.message(Command("id"))
        async def id_cmd(message: types.Message):
            await message.answer(f"🆔 ID экземпляра: `{INSTANCE_ID}`")
        
        @self.dp.message()
        async def handle_message(message: types.Message):
            if not message.text or message.text.startswith('/'):
                return
            
            await self.bot.send_chat_action(message.chat.id, "typing")
            await asyncio.sleep(0.5)
            
            print(f"📥 Запрос: '{message.text}'")
            
            try:
                prediction = await self.get_prediction(message.text)
                await message.answer(prediction, parse_mode="Markdown")
                print(f"✅ Ответ отправлен")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                await message.answer(
                    f"⚽ **{message.text}**\n\n"
                    f"Прогноз: **{random.choice(['2-1', '1-0', '1-1', '2-0'])}**\n"
                    f"Вероятный победитель: **Одна из команд**\n\n"
                    f"💡 *Локальный анализ*",
                    parse_mode="Markdown"
                )
    
    async def get_prediction(self, match_name):
        """Получить прогноз - сначала Gemini, потом локальный"""
        # 1. Пробуем Gemini
        gemini_result = await self.try_gemini(match_name)
        if gemini_result:
            return gemini_result
        
        # 2. Локальный прогноз
        return self.local_prediction(match_name)
    
    async def try_gemini(self, match_name):
        """Попытка получить прогноз от Gemini"""
        model = "gemini-flash-latest"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={AI_KEY}"
        
        prompt = f"""Футбольный матч: {match_name}. 
        Краткий прогноз: кто победит, какой счет, 2-3 ключевых фактора. 
        Отвечай очень кратко, 3-4 предложения."""
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 200}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        return f"🤖 **GEMINI AI ПРОГНОЗ**\n\n{text}\n\n📅 *{datetime.now().strftime('%H:%M')}*"
        except:
            pass
        
        return None
    
    def local_prediction(self, match_name):
        """Локальный прогноз"""
        # Простые правила
        match_lower = match_name.lower()
        
        # Известные исходы
        outcomes = {
            'эвертон лидс': ('Эвертон', '2-1', ['Домашний стадион', 'Опыт Дайча']),
            'лидс эвертон': ('Эвертон', '2-0', ['Качество состава', 'Мотивация']),
            'барселона реал': ('Реал Мадрид', '2-1', ['Форма Винисиуса', 'Класс']),
            'реал барселона': ('Реал Мадрид', '3-1', ['Атака Реала', 'Защита Барсы']),
            'арсенал челси': ('Арсенал', '2-0', ['Форма', 'Молодость']),
            'челси арсенал': ('Арсенал', '1-0', ['Дисциплина', 'Контроль']),
            'манчестер ливерпуль': ('Ливерпуль', '1-2', ['Прессинг', 'Салах']),
            'ливерпуль манчестер': ('Ливерпуль', '2-0', ['Энфилд', 'Клопп']),
            'зенит спартак': ('Зенит', '2-0', ['Качество', 'Стабильность']),
            'спартак зенит': ('Зенит', '1-2', ['Легионеры', 'Опыт']),
        }
        
        for key, (winner, score, factors) in outcomes.items():
            if key in match_lower:
                factors_text = '\n'.join([f'• {f}' for f in factors])
                return (
                    f"⚽ **МАТЧ:** {match_name}\n\n"
                    f"🏆 **ПОБЕДИТЕЛЬ:** {winner}\n"
                    f"📍 **СЧЕТ:** {score}\n\n"
                    f"🔑 **ФАКТОРЫ:**\n{factors_text}\n\n"
                    f"📊 *Локальный анализ*"
                )
        
        # Случайный прогноз
        teams = match_name.split()
        team1 = teams[0].title() if teams else "Команда А"
        team2 = teams[1].title() if len(teams) > 1 else "Команда Б"
        
        winner = random.choice([team1, team2])
        score = random.choice(["1-0", "2-0", "2-1", "1-1", "0-0", "3-1"])
        factors = random.sample([
            "Текущая форма", "Травмы", "Мотивация", 
            "Тактика", "История", "Стадион"
        ], 2)
        
        factors_text = '\n'.join([f'• {f}' for f in factors])
        
        return (
            f"⚽ **МАТЧ:** {match_name}\n\n"
            f"🏆 **ПОБЕДИТЕЛЬ:** {winner}\n"
            f"📍 **СЧЕТ:** {score}\n\n"
            f"🔑 **ФАКТОРЫ:**\n{factors_text}\n\n"
            f"📊 *Локальный анализ*"
        )
    
    async def force_kill_other_instances(self):
        """Пытаемся убить другие экземпляры"""
        print("🔫 Пытаюсь убить другие экземпляры...")
        
        # Создаем специальный бот для убийства
        killer_bot = Bot(token=TOKEN)
        
        try:
            # Жесткий метод: устанавливаем вебхук с force
            await killer_bot.set_webhook(
                url=f"https://kill-{INSTANCE_ID}.com",
                drop_pending_updates=True,
                max_connections=1
            )
            
            # Ждем
            await asyncio.sleep(3)
            
            # Удаляем вебхук
            await killer_bot.delete_webhook(drop_pending_updates=True)
            
            print("✅ Другие экземпляры должны быть убиты")
            
        finally:
            await killer_bot.session.close()
        
        # Ждем еще
        await asyncio.sleep(5)
    
    async def start(self):
        """Запуск бота"""
        # 1. Убиваем другие экземпляры
        await self.force_kill_other_instances()
        
        # 2. Очистка
        await self.bot.delete_webhook(drop_pending_updates=True)
        await asyncio.sleep(3)
        
        print(f"✅ Бот {INSTANCE_ID} готов")
        print("📱 Отправьте /start в Telegram")
        print("=" * 60)
        
        # 3. Запускаем с уникальными параметрами
        try:
            await self.dp.start_polling(
                self.bot,
                skip_updates=True,
                allowed_updates=["message"],
                polling_timeout=120,  # Очень большой таймаут
                relax=1,  # Большая задержка
                handle_signals=False  # Сами обрабатываем
            )
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            print(f"\n🛑 Бот {INSTANCE_ID} остановлен")

def signal_handler(signum, frame):
    """Обработчик Ctrl+C"""
    print(f"\n🚨 Получен сигнал {signum}. Завершаю бота {INSTANCE_ID}...")
    sys.exit(0)

async def main():
    """Точка входа"""
    # Регистрируем обработчик Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем бота
    football_bot = FootballBot()
    await football_bot.start()

if __name__ == "__main__":
    # Настройка для Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Запускаем
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Бот {INSTANCE_ID} завершен")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
