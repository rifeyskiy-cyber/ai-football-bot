import asyncio
import aiohttp
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
import sys

# === ВАШИ КЛЮЧИ ===
TOKEN = "8464793187:AAHErGkpbQUSF9HjfU1efmM0bgtFemmHb9E"
AI_KEY = "AIzaSyDQsQynmKLfiQCwXyfsqNB45a7ctSwCjyA"
# ===================

# Логирование
logging.basicConfig(level=logging.INFO, format="[BOT] %(message)s")

# Глобальная переменная для блокировки
bot_lock = None

async def create_singleton_bot():
    """Создает бота с защитой от множественных запусков"""
    global bot_lock
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Создаем файловую блокировку
    import os
    lock_file = "/tmp/football_bot.lock"
    
    try:
        # Пытаемся создать lock файл
        fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        bot_lock = fd
        print("🔒 Блокировка установлена - этот экземпляр главный")
    except FileExistsError:
        print("❌ Другой экземпляр уже запущен. Завершаюсь...")
        sys.exit(1)
    
    @dp.message(Command("start"))
    async def start_cmd(message: types.Message):
        await message.answer(
            "⚽ **Футбольный аналитик** 🤖\n\n"
            "Отправьте матч для анализа:\n"
            "• `Эвертон Лидс`\n"
            "• `Барселона Реал`\n"
            "• `Арсенал Челси`\n\n"
            "✅ AI активен!",
            parse_mode="Markdown"
        )
    
    @dp.message(Command("stop"))
    async def stop_cmd(message: types.Message):
        """Команда для остановки бота"""
        await message.answer("🛑 Останавливаю бота...")
        # Освобождаем блокировку
        if bot_lock:
            os.close(bot_lock)
            os.unlink(lock_file)
        sys.exit(0)
    
    @dp.message()
    async def handle_message(message: types.Message):
        if not message.text or message.text.startswith('/'):
            return
        
        await bot.send_chat_action(message.chat.id, "typing")
        await asyncio.sleep(0.5)
        
        print(f"📥 Запрос: {message.text}")
        
        # Простой AI запрос
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={AI_KEY}"
            prompt = f"Футбольный матч {message.text}. Краткий прогноз кто победит и счёт. Ответь на русском."
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ai_text = data['candidates'][0]['content']['parts'][0]['text']
                        response = f"🤖 **AI ПРОГНОЗ:**\n\n{ai_text}"
                    else:
                        response = f"⚽ **{message.text}**\n\nПрогноз: **{random.choice(['2-1', '1-0', '1-1'])}**"
        except:
            response = f"⚽ **{message.text}**\n\nПрогноз: **{random.choice(['2-1', '1-0', '1-1'])}**"
        
        await message.answer(response, parse_mode="Markdown")
    
    return bot, dp

async def main():
    """Главная функция"""
    print("=" * 50)
    print("🚀 ЗАПУСК ФУТБОЛЬНОГО БОТА (Синглтон)")
    print("=" * 50)
    
    # Останавливаем все предыдущие процессы
    print("🛑 Останавливаю возможные дубликаты...")
    try:
        # Прямой запрос к API для удаления вебхука
        import requests
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=5)
        print("✅ Старые соединения сброшены")
    except:
        pass
    
    # Ждем 5 секунд
    await asyncio.sleep(5)
    
    # Создаем бота с блокировкой
    bot, dp = await create_singleton_bot()
    
    # Очищаем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("✅ Бот готов к работе!")
    print("📱 Напишите /start в Telegram")
    print("=" * 50)
    
    # Запускаем polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен по запросу")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        # Очистка блокировки
        import os
        lock_file = "/tmp/football_bot.lock"
        if os.path.exists(lock_file):
            os.unlink(lock_file)
        print("🔒 Блокировка снята")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Завершение работы")
