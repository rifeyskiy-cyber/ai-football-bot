import asyncio
import aiohttp
import random
import json
import os
import logging
import hashlib
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from collections import defaultdict
from functools import lru_cache

# === КОНФИГУРАЦИЯ ===
# Убедитесь, что эти переменные заданы в настройках вашего хостинга (Koyeb)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
AI_KEY = os.getenv("GOOGLE_AI_KEY", "")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === БАЗА ДАННЫХ КОМАНД ===
FOOTBALL_DATA = {
    "эвертон": {
        "full_name": "Эвертон",
        "league": "АПЛ",
        "position": 14,
        "points": 25,
        "matches": 23,
        "wins": 7,
        "draws": 4,
        "losses": 12,
        "goals_for": 28,
        "goals_against": 39,
        "goal_difference": -11,
        "form": ["L", "W", "D", "L", "W", "L", "D"],
        "last_matches": [
            {"opponent": "Ман Сити", "result": "L", "score": "1-3", "date": "2026-01-25"},
            {"opponent": "Тоттенхэм", "result": "W", "score": "2-1", "date": "2026-01-18"},
            {"opponent": "Челси", "result": "D", "score": "0-0", "date": "2026-01-11"}
        ],
        "key_players": [
            {"name": "Доминик Калверт-Льюин", "position": "Нападающий", "status": "готов", "goals": 8},
            {"name": "Абдулай Дукуре", "position": "Полузащитник", "status": "травма", "return": "2 недели"}
        ],
        "coach": "Шон Дайч",
        "stadium": "Гудисон Парк",
        "avg_goals_for": 1.22,
        "avg_goals_against": 1.70,
        "clean_sheets": 4,
        "failed_to_score": 7
    },
    "лидс": {
        "full_name": "Лидс Юнайтед",
        "league": "Чемпионшип",
        "position": 3,
        "points": 52,
        "matches": 28,
        "wins": 15,
        "draws": 7,
        "losses": 6,
        "goals_for": 48,
        "goals_against": 32,
        "goal_difference": 16,
        "form": ["W", "D", "W", "L", "W", "D", "W"],
        "last_matches": [
            {"opponent": "Сандерленд", "result": "W", "score": "2-0", "date": "2026-01-24"}
        ],
        "key_players": [
            {"name": "Криассио Сомервилль", "position": "Нападающий", "status": "готов", "goals": 12}
        ],
        "coach": "Даниэль Фарке",
        "stadium": "Элланд Роуд",
        "avg_goals_for": 1.71,
        "avg_goals_against": 1.14,
        "clean_sheets": 10,
        "failed_to_score": 4
    },
    "арсенал": {
        "full_name": "Арсенал",
        "league": "АПЛ",
        "position": 2,
        "points": 56,
        "matches": 24,
        "wins": 17,
        "draws": 5,
        "losses": 2,
        "goals_for": 52,
        "goals_against": 22,
        "goal_difference": 30,
        "form": ["W", "W", "W", "D", "W", "L", "W"],
        "last_matches": [
            {"opponent": "Ливерпуль", "result": "W", "score": "2-1", "date": "2026-01-26"}
        ],
        "key_players": [
            {"name": "Букайо Сака", "position": "Нападающий", "status": "готов", "goals": 14},
            {"name": "Мартин Эдегор", "position": "Полузащитник", "status": "готов", "assists": 9}
        ],
        "coach": "Микель Артета",
        "stadium": "Эмирейтс",
        "avg_goals_for": 2.17,
        "avg_goals_against": 0.92,
        "clean_sheets": 12,
        "failed_to_score": 3
    }
}

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def normalize_value(value, min_val, max_val):
    if max_val == min_val: return 50
    return ((value - min_val) / (max_val - min_val)) * 100

def analyze_form(form_array):
    form_points = {"W": 3, "D": 1, "L": 0}
    points = sum(form_points.get(result, 0) for result in form_array)
    percentage = (points / (len(form_array) * 3)) * 100
    
    recent = form_array[:3]
    if all(r == "W" for r in recent): trend = "📈 Отличная"
    elif all(r == "L" for r in recent): trend = "📉 Плохая"
    else: trend = "➡️ Стабильная"
    
    return {"points": points, "percentage": round(percentage, 1), "trend": trend}

def calculate_match_stats(team1, team2):
    form1 = analyze_form(team1["form"])
    form2 = analyze_form(team2["form"])
    
    # Расчет вероятностей на основе формы и разницы мячей
    rating1 = (form1["percentage"] * 0.5) + (team1["goal_difference"] * 2)
    rating2 = (form2["percentage"] * 0.5) + (team2["goal_difference"] * 2)
    
    # Сдвиг для избежания отрицательных чисел
    min_rating = min(rating1, rating2)
    offset = abs(min_rating) + 10 if min_rating <= 0 else 0
    
    total = (rating1 + offset) + (rating2 + offset)
    win1 = round(((rating1 + offset) / total) * 100, 1)
    win2 = round(((rating2 + offset) / total) * 100, 1)
    draw = round(max(5, 30 - abs(win1 - win2)), 1)
    
    # Прогноз счета на основе среднего xG
    score1 = round((team1["avg_goals_for"] + team2["avg_goals_against"]) / 2)
    score2 = round((team2["avg_goals_for"] + team1["avg_goals_against"]) / 2)
    
    return {
        "probabilities": {"team1_win": win1, "draw": draw, "team2_win": win2},
        "predicted_score": f"{score1}-{score2}",
        "team1_stats": team1, "team2_stats": team2,
        "form1": form1, "form2": form2
    }

def get_team_data(name):
    name = name.lower().strip()
    return FOOTBALL_DATA.get(name) or FOOTBALL_DATA.get("эвертон") # Заглушка, если не найдено

async def get_ai_enhanced_prediction(match_name, stats):
    if not AI_KEY: return "AI Ключ не настроен."
    
    prompt = f"Анализ матча {match_name}. П1: {stats['probabilities']['team1_win']}%, Ничья: {stats['probabilities']['draw']}%, П2: {stats['probabilities']['team2_win']}%. Прогноз счета: {stats['predicted_score']}. Дай краткий экспертный комментарий."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={AI_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logger.error(f"AI Error: {e}")
    return "Не удалось получить AI аналитику."

# === ОБРАБОТЧИКИ КОМАНД ===

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("⚽ Привет! Напиши названия двух команд через пробел (например: Арсенал Эвертон), чтобы получить прогноз.")

@dp.message(Command("stats"))
async def stats_cmd(message: Message):
    args = message.text.split()[1:]
    if not args:
        await message.answer("Укажите команду: /stats Эвертон")
        return
    
    team = get_team_data(args[0])
    res = f"📊 *{team['full_name']}*\nПозиция: {team['position']}\nОчки: {team['points']}\nФорма: {' '.join(team['form'])}\n"
    
    # ИСПРАВЛЕННЫЙ ЦИКЛ (Строка 504)
    if team['last_matches']:
        res += "\n📅 *Последние игры:*\n"
        for m in team['last_matches']:
            res += f"• {m['opponent']} ({m['score']}) - {m['result']}\n"
            
    await message.answer(res, parse_mode="Markdown")

@dp.message(Command("form"))
async def form_cmd(message: Message):
    args = message.text.split()[1:]
    # ИСПРАВЛЕННЫЙ БЛОК (Строка 514)
    if not args:
        await message.answer("Укажите команду: /form Лидс")
        return
        
    team = get_team_data(args[0])
    analysis = analyze_form(team['form'])
    await message.answer(f"📈 *Форма {team['full_name']}*\nТренд: {analysis['trend']}\nЭффективность: {analysis['percentage']}%")

@dp.message(F.text)
async def analyze_match_message(message: Message):
    parts = message.text.split()
    if len(parts) < 2: return

    t1_data = get_team_data(parts[0])
    t2_data = get_team_data(parts[1])
    
    stats = calculate_match_stats(t1_data, t2_data)
    ai_text = await get_ai_enhanced_prediction(f"{t1_data['full_name']} - {t2_data['full_name']}", stats)
    
    response = (
        f"⚽ *{t1_data['full_name']} vs {t2_data['full_name']}*\n\n"
        f"📊 *Вероятности:*\n"
        f"П1: {stats['probabilities']['team1_win']}% | Х: {stats['probabilities']['draw']}% | П2: {stats['probabilities']['team2_win']}%\n"
        f"🎯 *Прогноз счета:* {stats['predicted_score']}\n\n"
        f"🧠 *AI Анализ:*\n{ai_text}"
    )
    await message.answer(response, parse_mode="Markdown")

# === ЗАПУСК ===
async def main():
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
