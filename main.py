import asyncio
import aiohttp
import random
import json
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
from collections import defaultdict
from functools import lru_cache
import hashlib

# === КОНФИГУРАЦИЯ ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8464793187:AAHnVesGUcKLcC8ih8lnhnOI7bIj_k_66CE")
AI_KEY = os.getenv("GOOGLE_AI_KEY", "AIzaSyDRwj6eXAP8XnXFx2CLEfuQc-R59XABKh4")



# Логирование
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
            {"opponent": "Челси", "result": "D", "score": "0-0", "date": "2026-01-11"},
            {"opponent": "Арсенал", "result": "L", "score": "1-2", "date": "2026-01-04"},
            {"opponent": "Ньюкасл", "result": "W", "score": "3-1", "date": "2025-12-28"},
            {"opponent": "Астон Вилла", "result": "L", "score": "0-2", "date": "2025-12-21"},
            {"opponent": "Вулверхэмптон", "result": "D", "score": "1-1", "date": "2025-12-14"}
        ],
        "key_players": [
            {"name": "Доминик Калверт-Льюин", "position": "Нападающий", "status": "готов", "goals": 8},
            {"name": "Джаред Брантуэйт", "position": "Защитник", "status": "готов", "apps": 20},
            {"name": "Джеймス Тарковски", "position": "Защитник", "status": "готов", "apps": 22},
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
        "goal_difference": +16,
        "form": ["W", "D", "W", "L", "W", "D", "W"],
        "last_matches": [
            {"opponent": "Сандерленд", "result": "W", "score": "2-0", "date": "2026-01-24"},
            {"opponent": "Ковентри", "result": "D", "score": "1-1", "date": "2026-01-17"},
            {"opponent": "Милуолл", "result": "W", "score": "3-1", "date": "2026-01-10"},
            {"opponent": "Норвич", "result": "L", "score": "0-1", "date": "2026-01-03"},
            {"opponent": "Престон", "result": "W", "score": "2-1", "date": "2025-12-27"},
            {"opponent": "Шеффилд Юнайтед", "result": "D", "score": "2-2", "date": "2025-12-20"},
            {"opponent": "Кардифф", "result": "W", "score": "3-0", "date": "2025-12-13"}
        ],
        "key_players": [
            {"name": "Криассио Сомервилль", "position": "Нападающий", "status": "готов", "goals": 12},
            {"name": "Джо Родон", "position": "Защитник", "status": "готов", "apps": 25},
            {"name": "Итан Ампаду", "position": "Полузащитник", "status": "готов", "apps": 27},
            {"name": "Джорджинио Раттер", "position": "Нападающий", "status": "под вопросом", "return": "неделя"}
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
        "goal_difference": +30,
        "form": ["W", "W", "W", "D", "W", "L", "W"],
        "last_matches": [
            {"opponent": "Ливерпуль", "result": "W", "score": "2-1", "date": "2026-01-26"},
            {"opponent": "Вест Хэм", "result": "W", "score": "3-0", "date": "2026-01-19"},
            {"opponent": "Манчестер Юнайтед", "result": "W", "score": "2-0", "date": "2026-01-12"},
            {"opponent": "Брайтон", "result": "D", "score": "1-1", "date": "2026-01-05"},
            {"opponent": "Вулверхэмптон", "result": "W", "score": "3-1", "date": "2025-12-29"},
            {"opponent": "Челси", "result": "L", "score": "0-1", "date": "2025-12-22"},
            {"opponent": "Астон Вилла", "result": "W", "score": "2-0", "date": "2025-12-15"}
        ],
        "key_players": [
            {"name": "Букайо Сака", "position": "Нападающий", "status": "готов", "goals": 14},
            {"name": "Мартин Эдегор", "position": "Полузащитник", "status": "готов", "assists": 9},
            {"name": "Уильям Салиба", "position": "Защитник", "status": "готов", "apps": 24},
            {"name": "Габриэл Жезус", "position": "Нападающий", "status": "под вопросом", "return": "3 дня"}
        ],
        "coach": "Микель Артета",
        "stadium": "Эмирейтс",
        "avg_goals_for": 2.17,
        "avg_goals_against": 0.92,
        "clean_sheets": 12,
        "failed_to_score": 3
    }
}

def normalize_value(value, min_val, max_val):
    """Нормализация значения от 0 до 100"""
    if max_val == min_val:
        return 50
    return ((value - min_val) / (max_val - min_val)) * 100

def analyze_form(form_array):
    """Анализ формы из последних 7 матчей"""
    form_points = {"W": 3, "D": 1, "L": 0}
    points = sum(form_points.get(result, 0) for result in form_array)
    max_points = 21  # 7 матчей * 3 очка
    
    form_percentage = (points / max_points) * 100
    
    # Определяем тренд
    recent_form = form_array[:3]  # Последние 3 матча
    if all(r == "W" for r in recent_form):
        trend = "📈 Отличная форма"
    elif all(r in ["W", "D"] for r in recent_form):
        trend = "↗️ Хорошая форма"
    elif all(r == "L" for r in recent_form):
        trend = "📉 Плохая форма"
    else:
        trend = "➡️ Нестабильная форма"
    
    return {
        "points": points,
        "percentage": round(form_percentage, 1),
        "trend": trend,
        "wins": form_array.count("W"),
        "draws": form_array.count("D"),
        "losses": form_array.count("L")
    }

def calculate_match_stats(team1_data, team2_data):
    """Расчет статистики для матча"""
    
    # Анализ формы
    form1 = analyze_form(team1_data["form"])
    form2 = analyze_form(team2_data["form"])
    
    # Сила атаки (забитые голы)
    attack_strength1 = team1_data["avg_goals_for"]
    attack_strength2 = team2_data["avg_goals_for"]
    
    # Сила защиты (пропущенные голы)
    defense_strength1 = team1_data["avg_goals_against"]
    defense_strength2 = team2_data["avg_goals_against"]
    
    # Прогнозируемые голы
    expected_goals1 = (attack_strength1 + defense_strength2) / 2
    expected_goals2 = (attack_strength2 + defense_strength1) / 2
    
    # Нормализация значений для рейтинга
    max_gd = max(abs(team1_data["goal_difference"]), abs(team2_data["goal_difference"]), 1)
    gd_normalized1 = normalize_value(team1_data["goal_difference"], -max_gd, max_gd)
    gd_normalized2 = normalize_value(team2_data["goal_difference"], -max_gd, max_gd)
    
    # Веса факторов
    form_weight = 0.4
    stats_weight = 0.4
    home_advantage = 0.2
    
    # Общий рейтинг
    rating1 = (form1["percentage"] * form_weight + 
               gd_normalized1 * stats_weight + 
               (home_advantage * 100 if team1_data.get("home", False) else 0))
    
    rating2 = (form2["percentage"] * form_weight + 
               gd_normalized2 * stats_weight + 
               (home_advantage * 100 if team2_data.get("home", False) else 0))
    
    # Вероятность победы
    total_rating = rating1 + rating2
    win_prob1 = (rating1 / total_rating) * 100
    win_prob2 = (rating2 / total_rating) * 100
    
    # Вероятность ничьей
    avg_defense = (defense_strength1 + defense_strength2) / 2
    draw_factor = max(0, 1 - avg_defense)
    draw_prob = min(35, draw_factor * 100)
    
    # Распределяем вероятность ничьей
    win_prob1 = win_prob1 * (1 - draw_prob/100)
    win_prob2 = win_prob2 * (1 - draw_prob/100)
    
    # Прогноз счета
    score1 = round(expected_goals1)
    score2 = round(expected_goals2)
    
    # Корректировка на основе формы
    form_diff = form1["percentage"] - form2["percentage"]
    if abs(form_diff) > 20:
        if form_diff > 0:
            score1 += 1
        else:
            score2 += 1
    
    # Ограничения
    score1 = max(0, min(5, score1))
    score2 = max(0, min(5, score2))
    
    # Наличие ключевых игроков
    available_players1 = sum(1 for p in team1_data["key_players"] if p["status"] == "готов")
    available_players2 = sum(1 for p in team2_data["key_players"] if p["status"] == "готов")
    
    return {
        "team1_stats": team1_data,
        "team2_stats": team2_data,
        "form1": form1,
        "form2": form2,
        "expected_goals": [expected_goals1, expected_goals2],
        "predicted_score": f"{score1}-{score2}",
        "probabilities": {
            "team1_win": round(win_prob1, 1),
            "draw": round(draw_prob, 1),
            "team2_win": round(win_prob2, 1)
        },
        "key_players_available": [available_players1, available_players2],
        "total_key_players": [len(team1_data["key_players"]), len(team2_data["key_players"])]
    }

def format_form_display(form_array):
    """Форматирование формы для отображения"""
    form_map = {"W": "✅", "D": "⚪", "L": "❌"}
    return " ".join(form_map.get(r, "❓") for r in form_array)

def create_stub_data(team_name):
    """Создание заглушки для неизвестной команды"""
    return {
        "full_name": team_name.title(),
        "league": "Неизвестно",
        "position": random.randint(1, 20),
        "points": random.randint(10, 50),
        "matches": random.randint(15, 30),
        "wins": random.randint(5, 15),
        "draws": random.randint(3, 10),
        "losses": random.randint(3, 15),
        "goals_for": random.randint(15, 45),
        "goals_against": random.randint(15, 45),
        "goal_difference": random.randint(-20, 20),
        "form": random.choices(["W", "D", "L"], k=7, weights=[0.4, 0.3, 0.3]),
        "last_matches": [],
        "key_players": [],
        "coach": "Неизвестный тренер",
        "stadium": "Неизвестный стадион",
        "avg_goals_for": round(random.uniform(0.8, 2.2), 2),
        "avg_goals_against": round(random.uniform(0.8, 2.2), 2),
        "clean_sheets": random.randint(2, 10),
        "failed_to_score": random.randint(2, 10)
    }

def get_team_data(team_name):
    """Получение данных о команде"""
    team_lower = team_name.lower().strip()
    
    # Точное совпадение
    if team_lower in FOOTBALL_DATA:
        return FOOTBALL_DATA[team_lower].copy()
    
    # Поиск по части названия
    for key, data in FOOTBALL_DATA.items():
        team_words = team_lower.split()
        key_words = key.split()
        
        # Если одно из слов совпадает
        if any(word in key for word in team_words) or any(word in team_lower for word in key_words):
            return data.copy()
    
    # Создание заглушки
    return create_stub_data(team_name)

def generate_hash(text):
    """Генерация хэша для кэширования"""
    return hashlib.md5(text.encode()).hexdigest()

@lru_cache(maxsize=100)
async def get_cached_ai_prediction(match_hash, prompt):
    """Кэшированный запрос к AI"""
    return await get_ai_enhanced_prediction_raw(prompt)

async def get_ai_enhanced_prediction_raw(prompt):
    """Запрос к AI API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={AI_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        return data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        logger.error(f"AI вернул пустой ответ: {data}")
                        return None
                else:
                    logger.error(f"AI ошибка HTTP {resp.status}: {await resp.text()}")
                    return None
    except asyncio.TimeoutError:
        logger.error("AI запрос превысил таймаут")
        return None
    except Exception as e:
        logger.error(f"AI ошибка: {e}")
        return None

async def get_ai_enhanced_prediction(match_name, stats_analysis):
    """Улучшенный прогноз с использованием AI"""
    try:
        prompt = f"""
        Ты профессиональный футбольный аналитик. Проанализируй матч: {match_name}
        
        СТАТИСТИКА КОМАНД:
        
        {stats_analysis['team1_stats']['full_name']}:
        - Турнир: {stats_analysis['team1_stats']['league']}
        - Позиция: {stats_analysis['team1_stats']['position']}-е место
        - Очки: {stats_analysis['team1_stats']['points']}
        - Забито/Пропущено: {stats_analysis['team1_stats']['goals_for']}-{stats_analysis['team1_stats']['goals_against']} (разница: {stats_analysis['team1_stats']['goal_difference']})
        - Форма (последние 7): {format_form_display(stats_analysis['team1_stats']['form'])}
        - Ключевые игроки: {stats_analysis['key_players_available'][0]}/{stats_analysis['total_key_players'][0]} в строю
        - Тренер: {stats_analysis['team1_stats']['coach']}
        
        {stats_analysis['team2_stats']['full_name']}:
        - Турнир: {stats_analysis['team2_stats']['league']}
        - Позиция: {stats_analysis['team2_stats']['position']}-е место
        - Очки: {stats_analysis['team2_stats']['points']}
        - Забито/Пропущено: {stats_analysis['team2_stats']['goals_for']}-{stats_analysis['team2_stats']['goals_against']} (разница: {stats_analysis['team2_stats']['goal_difference']})
        - Форма (последние 7): {format_form_display(stats_analysis['team2_stats']['form'])}
        - Ключевые игроки: {stats_analysis['key_players_available'][1]}/{stats_analysis['total_key_players'][1]} в строю
        - Тренер: {stats_analysis['team2_stats']['coach']}
        
        СТАТИСТИЧЕСКИЙ АНАЛИЗ:
        - Ожидаемые голы: {stats_analysis['team1_stats']['full_name']} {stats_analysis['expected_goals'][0]:.1f} - {stats_analysis['team2_stats']['full_name']} {stats_analysis['expected_goals'][1]:.1f}
        - Вероятность победы: {stats_analysis['team1_stats']['full_name']} {stats_analysis['probabilities']['team1_win']}%, Ничья {stats_analysis['probabilities']['draw']}%, {stats_analysis['team2_stats']['full_name']} {stats_analysis['probabilities']['team2_win']}%
        - Прогнозируемый счет: {stats_analysis['predicted_score']}
        
        Дай краткий анализ (3-4 предложения) с учетом:
        1. Текущей формы команд
        2. Турнирной мотивации
        3. Состава (ключевые игроки)
        4. Тактического противостояния тренеров
        
        Будь конкретным и профессиональным. Не упоминай, что ты ИИ.
        """
        
        # Генерируем хэш для кэширования
        match_hash = generate_hash(prompt)
        
        # Пробуем получить из кэша
        ai_analysis = await get_cached_ai_prediction(match_hash, prompt)
        
        if not ai_analysis:
            # Если кэш пустой, делаем новый запрос
            ai_analysis = await get_ai_enhanced_prediction_raw(prompt)
        
        return ai_analysis
        
    except Exception as e:
        logger.error(f"Ошибка в AI анализе: {e}")
        return None

def generate_stats_table(team_data):
    """Генерация таблицы статистики"""
    return f"""
📊 *ОСНОВНАЯ СТАТИСТИКА:*
╭────────────────┬──────────────╮
│ Показатель     │ Значение     │
├────────────────┼──────────────┤
│ Лига           │ {team_data['league']}
│ Позиция        │ {team_data['position']}-е место
│ Очки           │ {team_data['points']}
│ Матчи          │ {team_data['matches']}
│ Победы/Ничьи/  │ {team_data['wins']}/{team_data['draws']}/{team_data['losses']}
│ Поражения      │              │
│ Забито         │ {team_data['goals_for']}
│ Пропущено      │ {team_data['goals_against']}
│ Разница голов  │ {team_data['goal_difference']:+d}
│ В ср. забивает │ {team_data['avg_goals_for']:.2f}
│ В ср. пропус-  │ {team_data['avg_goals_against']:.2f}
│ кает           │              │
│ Сухие матчи    │ {team_data['clean_sheets']}
│ Не забивали    │ {team_data['failed_to_score']}
╰────────────────┴──────────────╯
"""

# ========== ОБРАБОТЧИКИ КОМАНД ==========

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "⚽ *ПРОФЕССИОНАЛЬНЫЙ ФУТБОЛЬНЫЙ АНАЛИТИК* 🤖\n\n"
        "🔍 *Анализирую матчи по 15+ параметрам:*\n"
        "• Форма команд (последние 7 матчей)\n"
        "• Турнирная таблица и позиция\n"
        "• Забитые/пропущенные голы\n"
        "• Наличие ключевых игроков\n"
        "• Статистика тренеров\n"
        "• Исторические показатели\n\n"
        "📝 *Отправьте матч в формате:*\n"
        "`Эвертон Лидс`\n\n"
        "📊 *Пример команды:*\n"
        "`/stats Эвертон` - детальная статистика\n"
        "`/form Лидс` - форма команды\n"
        "`/players Арсенал` - состав\n"
        "`/help` - справка по командам",
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "📋 *СПРАВКА ПО КОМАНДАМ:*\n\n"
        "⚽ *Анализ матча:*\n"
        "Просто отправьте названия двух команд через пробел\n"
        "Пример: `Эвертон Лидс`\n\n"
        "📊 *Другие команды:*\n"
        "`/stats [команда]` - детальная статистика\n"
        "`/form [команда]` - форма команды\n"
        "`/players [команда]` - состав и травмы\n"
        "`/start` - начальное сообщение\n"
        "`/help` - эта справка",
        parse_mode="Markdown"
    )

@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    """Детальная статистика команды"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        await message.answer("⚠️ Укажите команду: `/stats Эвертон`", parse_mode="Markdown")
        return
    
    team_name = " ".join(args)
    team_data = get_team_data(team_name)
    
    response = f"""
🏆 *{team_data['full_name'].upper()}*

{generate_stats_table(team_data)}

👨‍🏫 *Тренер:* {team_data['coach']}
🏟️ *Стадион:* {team_data['stadium']}

📈 *ФОРМА (последние 7 матчей):*
{format_form_display(team_data['form'])}
"""
    
    # Последние матчи
    if team_data['last_matches']:
        response += "\n📅 *ПОСЛЕДНИЕ МАТЧИ:*\n"
        for match in team_data['last_matches'][:3]:  # Последние 3
            result_emoji = {"W": "✅", "D": "⚪", "L": "❌"}.get(match['result'], "❓")
            response += f"{result_emoji} {match['opponent']} {match['score']} ({match['date']})\n"
    
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("form"))
async def form_cmd(message: types.Message):
    """Форма команды"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
   
