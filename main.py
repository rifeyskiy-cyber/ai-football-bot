import asyncio
import aiohttp
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

# === КОНФИГУРАЦИЯ ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8464793187:AAEb2-OgN8ZEM64kr-2wj9TqZRXnidWHmpc")
AI_KEY = os.getenv("GOOGLE_AI_KEY", "AIzaSyBEc7T2HzCplYSNcv0d-X8aYZ_K35ZlUMo")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === БАЗА ДАННЫХ ===
# league_rank: АПЛ = 1.0, Чемпионшип = 0.85 (смягчено для баланса)
FOOTBALL_DATA = {
    "эвертон": {
        "full_name": "Эвертон", "league": "АПЛ", "league_rank": 1.0,
        "position": 14, "points": 25, "goal_difference": -11,
        "form": ["L", "W", "D", "L", "W", "L", "D"],
        "avg_goals_for": 1.22, "avg_goals_against": 1.70
    },
    "лидс": {
        "full_name": "Лидс Юнайтед", "league": "Чемпионшип", "league_rank": 0.85,
        "position": 3, "points": 52, "goal_difference": 16,
        "form": ["W", "D", "W", "L", "W", "D", "W"],
        "avg_goals_for": 1.71, "avg_goals_against": 1.14
    },
    "арсенал": {
        "full_name": "Арсенал", "league": "АПЛ", "league_rank": 1.0,
        "position": 2, "points": 56, "goal_difference": 30,
        "form": ["W", "W", "W", "D", "W", "L", "W"],
        "avg_goals_for": 2.17, "avg_goals_against": 0.92
    }
}

# === ЛОГИКА АНАЛИЗА ===

def calculate_match_stats(team1, team2):
    def get_form_score(f_array):
        pts = sum({"W": 3, "D": 1, "L": 0}.get(r, 0) for r in f_array)
        return (pts / (len(f_array) * 3)) * 100

    # Расчет базовой силы с учетом веса лиги
    power1 = (team1["league_rank"] * 70) + (get_form_score(team1["form"]) * 0.15) + (team1["goal_difference"] * 0.3)
    power2 = (team2["league_rank"] * 70) + (get_form_score(team2["form"]) * 0.15) + (team2["goal_difference"] * 0.3)

    diff = power1 - power2
    
    # Расчет вероятностей (более плавный)
    win1_prob = 37 + (diff * 1.2)
    win2_prob = 37 - (diff * 1.2)
    
    # Удерживаем вероятности в разумных пределах (5% - 85%)
    win1_prob = max(5, min(85, win1_prob))
    win2_prob = max(5, min(85, win2_prob))
    draw_prob = 100 - win1_prob - win2_prob

    # Прогноз счета
    score1 = round((team1["avg_goals_for"] + team2["avg_goals_against"]) / 2 + (0.4 if diff > 5 else 0))
    score2 = round((team2["avg_goals_for"] + team1["avg_goals_against"]) / 2 + (0.4 if diff < -5 else 0))

    return {
        "win1": round(win1_prob, 1), "draw": round(draw_prob, 1), "win2": round(win2_prob, 1),
        "score": f"{score1}-{score2}"
    }

async def get_ai_prediction(t1, t2, stats):
    if not AI_KEY: return "AI Ключ не настроен в переменных окружения."
    
    # Исходный URL из ваших логов
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={AI_KEY}"
    
    prompt = (f"Проанализируй футбольный матч {t1['full_name']} vs {t2['full_name']}. "
              f"Математические шансы: П1 {stats['win1']}%, Ничья {stats['draw']}%, П2 {stats['win2']}%. "
              f"Ожидаемый счет: {stats['score']}. Напиши краткое экспертное мнение (2 фразы).")
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"Ошибка AI (Статус: {resp.status}). Проверьте API ключ."
    except Exception as e:
        logger.error(f"AI Connection Error: {e}")
        return "Аналитика временно недоступна (ошибка соединения)."

# === ОБРАБОТЧИКИ ===

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("⚽ Бот готов к работе. Напишите две команды из базы (например: Эвертон Лидс) для получения прогноза.")

@dp.message(F.text)
async def analyze(message: Message):
    parts = message.text.lower().split()
    if len(parts) < 2: 
        return

    t1 = FOOTBALL_DATA.get(parts[0])
    t2 = FOOTBALL_DATA.get(parts[1])

    if not t1 or not t2:
        await message.answer("❌ Ошибка: Одна или обе команды не найдены в базе данных.")
        return

    stats = calculate_match_stats(t1, t2)
    ai_text = await get_ai_prediction(t1, t2, stats)

    res = (f"⚽ *{t1['full_name']}* vs *{t2['full_name']}*\n\n"
           f"📊 *Математический прогноз:*\n"
           f"П1: {stats['win1']}% | X: {stats['draw']}% | П2: {stats['win2']}%\n"
           f"🎯 *Прогноз счета:* {stats['score']}\n\n"
           f"🧠 *Мнение AI:*\n{ai_text}")
    
    await message.answer(res, parse_mode="Markdown")

async def main():
    logger.info("Запуск polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот выключен.")
        
