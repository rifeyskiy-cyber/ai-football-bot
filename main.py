import asyncio
import aiohttp
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from typing import Optional, Dict

# === КОНФИГУРАЦИЯ ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8464793187:AAEb2-OgN8ZEM64kr-2wj9TqZRXnidWHmpc")
AI_KEY = os.getenv("GOOGLE_AI_KEY", "AIzaSyBEc7T2HzCplYSNcv0d-X8aYZ_K35ZlUMo")

# Валидация ключей
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
if not AI_KEY:
    print("⚠️ GOOGLE_AI_KEY не установлен - AI функция отключена")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === КОНФИГУРАЦИЯ РАСЧЁТОВ ===
CALCULATION_CONFIG = {
    "league_weight": 100,
    "form_weight": 0.1,
    "goal_diff_weight": 0.2,
    "win_prob_weight": 0.5,
    "goal_boost": 0.3,
    "diff_threshold": 5,
    "min_win_prob": 10,
    "max_win_prob": 80,
}

# === БАЗА ДАННЫХ ===
FOOTBALL_DATA = {
    "эвертон": {
        "full_name": "Эвертон", "league": "АПЛ", "league_rank": 1.0,
        "position": 14, "goal_difference": -11,
        "form": ["L", "W", "D", "L", "W", "L", "D"],
        "avg_goals_for": 1.22, "avg_goals_against": 1.70
    },
    "лидс": {
        "full_name": "Лидс Юнайтед", "league": "Чемпионшип", "league_rank": 0.8,
        "position": 3, "goal_difference": 16,
        "form": ["W", "D", "W", "L", "W", "D", "W"],
        "avg_goals_for": 1.71, "avg_goals_against": 1.14
    },
    "арсенал": {
        "full_name": "Арсенал", "league": "АПЛ", "league_rank": 1.0,
        "position": 2, "goal_difference": 30,
        "form": ["W", "W", "W", "D", "W", "L", "W"],
        "avg_goals_for": 2.17, "avg_goals_against": 0.92
    }
}

# === ЛОГИКА АНАЛИЗА ===

def get_form_score(form: list) -> float:
    """Расчёт процента баллов из последних матчей (0-100)"""
    points = sum({"W": 3, "D": 1, "L": 0}.get(r, 0) for r in form)
    return (points / (len(form) * 3)) * 100

def calculate_team_power(team: Dict) -> float:
    """Расчёт силы команды"""
    cfg = CALCULATION_CONFIG
    return (
        team["league_rank"] * cfg["league_weight"] +
        get_form_score(team["form"]) * cfg["form_weight"] +
        team["goal_difference"] * cfg["goal_diff_weight"]
    )

def calculate_match_stats(team1: Dict, team2: Dict) -> Dict:
    """Расчёт статистики матча"""
    cfg = CALCULATION_CONFIG
    
    power1 = calculate_team_power(team1)
    power2 = calculate_team_power(team2)
    diff = power1 - power2
    
    # Вероятности (33.3% за базовый + влияние силы)
    win1_prob = 33.3 + (diff * cfg["win_prob_weight"])
    win2_prob = 33.3 - (diff * cfg["win_prob_weight"])
    
    # Корректировка границ
    win1_prob = max(cfg["min_win_prob"], min(cfg["max_win_prob"], win1_prob))
    win2_prob = max(cfg["min_win_prob"], min(cfg["max_win_prob"], win2_prob))
    draw_prob = 100 - win1_prob - win2_prob
    
    # Прогноз счета
    score1 = round(
        (team1["avg_goals_for"] + team2["avg_goals_against"]) / 2 +
        (cfg["goal_boost"] if diff > cfg["diff_threshold"] else 0)
    )
    score2 = round(
        (team2["avg_goals_for"] + team1["avg_goals_against"]) / 2 +
        (cfg["goal_boost"] if diff < -cfg["diff_threshold"] else 0)
    )
    
    return {
        "win1": round(win1_prob, 1),
        "draw": round(draw_prob, 1),
        "win2": round(win2_prob, 1),
        "score": f"{score1}-{score2}",
        "power_diff": round(diff, 2)
    }

async def get_ai_prediction(t1: Dict, t2: Dict, stats: Dict) -> str:
    """Получение прогноза от AI"""
    if not AI_KEY:
        return "🤖 AI анализ недоступен (не установлен API ключ)"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    prompt = (
        f"Футбол: {t1['full_name']} (лига: {t1['league']}) vs "
        f"{t2['full_name']} (лига: {t2['league']}). "
        f"Вероятности: П1 {stats['win1']}%, Ничья {stats['draw']}%, П2 {stats['win2']}%. "
        f"Прогноз счёта: {stats['score']}. "
        f"Напиши краткий экспертный прогноз в 2-3 предложениях."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                params={"key": AI_KEY},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        return data['candidates'][0]['content']['parts'][0]['text']
                    except (KeyError, IndexError, TypeError) as e:
                        logger.error(f"Ошибка парсинга AI ответа: {e}")
                        return "⚠️ Ошибка обработки AI ответа"
                else:
                    logger.error(f"AI API вернул статус {resp.status}")
                    return f"⚠️ Ошибка AI API (статус {resp.status})"
                    
    except asyncio.TimeoutError:
        logger.warning("Timeout при запросе к AI")
        return "⏱️ Timeout AI анализа"
    except Exception as e:
        logger.error(f"Ошибка при запросе к AI: {e}")
        return "❌ Ошибка подключения к AI"

# === ОБРАБОТЧИКИ ===

@dp.message(Command("start"))
async def start(message: Message):
    """Стартовое сообщение"""
    teams = ", ".join([f"*{k.capitalize()}*" for k in FOOTBALL_DATA.keys()])
    await message.answer(
        f"⚽ *Прогноз матчей*\n\n"
        f"Напишите две команды через пробел:\n"
        f"{teams}\n\n"
        f"Пример: `эвертон арсенал`",
        parse_mode="Markdown"
    )

@dp.message(Command("teams"))
async def teams_list(message: Message):
    """Список доступных команд"""
    teams_info = "\n".join([
        f"• *{data['full_name']}* ({data['league']}, позиция {data['position']})"
        for data in FOOTBALL_DATA.values()
    ])
    await message.answer(f"📋 *Доступные команды:*\n\n{teams_info}", parse_mode="Markdown")

@dp.message(F.text)
async def analyze(message: Message):
    """Анализ матча"""
    parts = message.text.lower().strip().split()
    
    if len(parts) < 2:
        await message.answer("❌ Укажите две команды (например: `эвертон арсенал`)")
        return
    
    t1 = FOOTBALL_DATA.get(parts[0])
    t2 = FOOTBALL_DATA.get(parts[1])
    
    if not t1 or not t2:
        available = ", ".join(FOOTBALL_DATA.keys())
        await message.answer(
            f"❌ Команда не найдена\n\n"
            f"Доступны: {available}\n\n"
            f"Используйте `/teams` для полного списка",
            parse_mode="Markdown"
        )
        return
    
    if t1 == t2:
        await message.answer("😅 Команда не может играть сама с собой!")
        return
    
    # Показываем, что думаем
    await message.chat.do("typing")
    
    stats = calculate_match_stats(t1, t2)
    ai_text = await get_ai_prediction(t1, t2, stats)
    
    response = (
        f"⚽ *{t1['full_name']}* vs *{t2['full_name']}*\n\n"
        f"📊 *Вероятности исходов:*\n"
        f"   П1 (победа 1): `{stats['win1']}%`\n"
        f"   X (ничья): `{stats['draw']}%`\n"
        f"   П2 (победа 2): `{stats['win2']}%`\n\n"
        f"🎯 *Прогноз счёта:* `{stats['score']}`\n\n"
        f"🧠 *Аналитика:*\n{ai_text}"
    )
    
    await message.answer(response, parse_mode="Markdown")

@dp.message()
async def fallback(message: Message):
    """Обработка неизвестных команд"""
    await message.answer(
        "🤔 Команда не распознана. Используйте `/start` для помощи",
        parse_mode="Markdown"
    )

async def main():
    """Запуск бота"""
    logger.info("🚀 Запуск бота...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⛔ Бот остановлен")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
