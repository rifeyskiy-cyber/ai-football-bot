async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print(f"--- ЗАПУСК СЕССИИ {session_id} ---")
    
    # Удаляем вебхук (если был) и пропускаем накопившиеся обновления
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук удален, старые обновления пропущены.")
    except Exception as e:
        print(f"⚠️ Ошибка при удалении вебхука: {e}")
    
    # Ждем немного
    await asyncio.sleep(2)
    
    print(f">>> БОТ {session_id} ГОТОВ <<<")
    print("Ожидание сообщений...")
    
    try:
        # ИСПРАВЛЕНИЕ: Добавляем skip_updates=True
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        if bot.session:
            await bot.session.close()
