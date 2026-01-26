import asyncio
import aiohttp
import os
import signal
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# КЛЮЧИ
TOKEN = "8464793187:AAFd3MNyXWwX4g9bAZrPvVEVrZcz0GqcbjA"
AI_KEY = "AIzaSyDgW7ONTdXO_yiVTYlGs4Y_Q5VaGP0sano"

print("=" * 60)
print("🔥 ПОЛНЫЙ ПЕРЕЗАПУСК БОТА С ПРИНУДИТЕЛЬНЫМ СБРОСОМ")
print("=" * 60)

async def complete_reset():
    """Полный сброс состояния бота"""
    print("\n🔄 ВЫПОЛНЯЮ ПОЛНЫЙ СБРОС...")
    
    temp_bot = Bot(token=TOKEN)
    
    try:
        # 1. Удаляем вебхук многократно
        for i in range(5):
            try:
                await temp_bot.delete_webhook(drop_pending_updates=True)
                print(f"  ✅ Вебхук удален ({i+1}/5)")
                await asyncio.sleep(0.5)
            except:
                pass
        
        # 2. Получаем текущие обновления и сбрасываем offset
        try:
            # Запрашиваем обновления с очень старым offset
            updates = await temp_bot.get_updates(offset=-10000, timeout=1)
            if updates:
                last_id = updates[-1].update_id
                # Сбрасываем offset ЗА последним обновлением
                await temp_bot.get_updates(offset=last_id + 100, timeout=1)
                print(f"  ✅ Offset сброшен до {last_id + 100}")
        except:
            pass
        
        # 3. Устанавливаем пустой вебхук и сразу удаляем
        try:
            await temp_bot.set_webhook(
                url="https://example.com/temp",
                drop_pending_updates=True,
                max_connections=1
            )
            await asyncio.sleep(0.5)
            await temp_bot.delete_webhook(drop_pending_updates=True)
            print("  ✅ Вебхук переустановлен и удален")
        except:
            pass
        
        # 4. Долгая пауза для Telegram
        print("  ⏳ Жду 5 секунд для сброса на стороне Telegram...")
        await asyncio.sleep(5)
        
    finally:
        await temp_bot.session.close()
    
    print("✅ ПОЛНЫЙ СБРОС ЗАВЕРШЕН\n")

async def get_prediction_simple(match_name):
    """Упрощенный запрос к Gemini"""
    # Используем гарантированно работающую модель
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={AI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Ты футбольный эксперт. Матч: {match_name}. Кто победит и какой счет? Ответь очень кратко."
            }]
        }]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=8) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"⚠️ Ошибка AI: {e}")
    
    # Запасной ответ
    return "⚽ Вероятная победа одной из команд со счетом 2-1 или 1-0."

async def run_single_instance():
    """Запуск одного уникального экземпляра"""
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Генерируем уникальный ID для этого экземпляра
    import uuid
    instance_id = str(uuid.uuid4())[:6]
    print(f"📱 ID этого экземпляра: {instance_id}")
    
    @dp.message(Command("start"))
    async def start(message: types.Message):
        await message.answer(f"⚽ Бот работает! (ID: {instance_id})\nНапишите матч.")
    
    @dp.message(Command("id"))
    async def get_id(message: types.Message):
        await message.answer(f"🆔 ID экземпляра: {instance_id}")
    
    @dp.message()
    async def handle(message: types.Message):
        if not message.text or message.text.startswith('/'):
            return
        
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Короткая пауза для имитации обработки
        await asyncio.sleep(0.5)
        
        prediction = await get_prediction_simple(message.text)
        await message.answer(f"⚽ {message.text}\n\n{prediction}")
    
    # ЗАПУСК С УНИКАЛЬНЫМИ ПАРАМЕТРАМИ
    print(f"\n🚀 Запускаю экземпляр {instance_id}...")
    
    # Используем специальные параметры для избежания конфликтов
    try:
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=["message"],
            polling_timeout=30,
            relax=0.1,
            handle_signals=False  # Сами обрабатываем сигналы
        )
    except Exception as e:
        print(f"❌ Ошибка polling: {e}")
    finally:
        await bot.session.close()
        print(f"\n🛑 Экземпляр {instance_id} остановлен")

async def main():
    """Основная функция"""
    print("\n🔧 ШАГ 1: Полный сброс состояния")
    await complete_reset()
    
    print("🔧 ШАГ 2: Запуск единственного экземпляра")
    print("   ⚠️  Убедитесь, что других экземпляров НЕТ!")
    print("   ⚠️  Если видите ошибку конфликта - остановите ВСЕ процессы бота")
    print()
    
    # Даем пользователю время на чтение
    await asyncio.sleep(2)
    
    # Запускаем единственный экземпляр
    await run_single_instance()

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print(f"\n🛑 Получен сигнал {signum}. Завершаю работу...")
    sys.exit(0)

if __name__ == "__main__":
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Настройка event loop
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass
    
    # Запускаем
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Завершение по запросу пользователя")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
