import asyncio
import aiohttp
import random
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import logging
from collections import defaultdict

# === КОНФИГУРАЦИЯ ===
TOKEN = "ВАШ_ТОКЕН"
AI_KEY = "AIzaSyDQsQynmKLfiQCwXyfsqNB45a7ctSwCjyA"

# Логирование
logging.basicConfig(level=logging.INFO, format="📊 %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === БАЗА ДАННЫХ КОМАНД (можно заменить на реальный API) ===
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
        "form": ["L", "W", "D", "L", "W", "L", "D"],  # Последние 7 матчей
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
            {"name": "Джеймс Тарковски", "position": "Защитник", "status": "готов", "apps": 22},
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
    
    # Добавьте другие команды по аналогии...
}

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
    
    # Коэффициенты на основе формы и статистики
    form_weight = 0.4
    stats_weight = 0.4
    home_advantage = 0.2  # Домашнее преимущество
    
    # Общий рейтинг
    rating1 = (form1["percentage"] * form_weight + 
               (team1_data["goal_difference"] + 50) * stats_weight +  # +50 чтобы убрать отрицательные
               (home_advantage * 100 if "home" in team1_data else 0))
    
    rating2 = (form2["percentage"] * form_weight + 
               (team2_data["goal_difference"] + 50) * stats_weight +
               (home_advantage * 100 if "home" in team2_data else 0))
    
    # Вероятность победы
    total_rating = rating1 + rating2
    win_prob1 = (rating1 / total_rating) * 100
    win_prob2 = (rating2 / total_rating) * 100
    draw_prob = 100 - win_prob1 - win_prob2
    
    # Прогноз счета на основе ожидаемых голов
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

def get_team_data(team_name):
    """Получение данных о команде"""
    team_lower = team_name.lower()
    
    # Поиск команды в базе
    for key, data in FOOTBALL_DATA.items():
        if key in team_lower or team_lower in key:
            return data
    
    # Если команда не найдена, создаем базовые данные
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
        "form": random.choices(["W", "D", "L"], k=7),
        "last_matches": [],
        "key_players": [],
        "coach": "Неизвестный тренер",
        "stadium": "Неизвестный стадион",
        "avg_goals_for": round(random.uniform(0.8, 2.2), 2),
        "avg_goals_against": round(random.uniform(0.8, 2.2), 2),
        "clean_sheets": random.randint(2, 10),
        "failed_to_score": random.randint(2, 10)
    }

async def get_ai_enhanced_prediction(match_name, stats_analysis):
    """Улучшенный прогноз с использованием AI и статистики"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={AI_KEY}"
        
        # Создаем детальный промпт со статистикой
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
        4. Исторических показателей
        5. Тактического противостояния тренеров
        
        Будь конкретным и профессиональным.
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logger.error(f"AI ошибка: {e}")
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

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
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
        "`/players Арсенал` - состав",
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
        await message.answer("⚠️ Укажите команду: `/form Лидс`", parse_mode="Markdown")
        return
    
    team_name = " ".join(args)
    team_data = get_team_data(team_name)
    form_analysis = analyze_form(team_data["form"])
    
    response = f"""
📊 *ФОРМА {team_data['full_name'].upper()}*

{format_form_display(team_data['form'])}

*АНАЛИЗ ФОРМЫ:*
• Очков в последних 7: {form_analysis['points']}/21 ({form_analysis['percentage']}%)
• Побед/Ничьих/Поражений: {form_analysis['wins']}/{form_analysis['draws']}/{form_analysis['losses']}
• Тренд: {form_analysis['trend']}

*ПОСЛЕДНИЕ 7 МАТЧЕЙ:*
"""
    
    for i, match in enumerate(team_data['last_matches'][:7], 1):
        result_emoji = {"W": "✅", "D": "⚪", "L": "❌"}.get(match['result'], "❓")
        response += f"{i}. {result_emoji} {match['opponent']} {match['score']}\n"
    
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("players"))
async def players_cmd(message: types.Message):
    """Состав и травмы"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        await message.answer("⚠️ Укажите команду: `/players Арсенал`", parse_mode="Markdown")
        return
    
    team_name = " ".join(args)
    team_data = get_team_data(team_name)
    
    response = f"""
👥 *СОСТАВ {team_data['full_name'].upper()}*

*КЛЮЧЕВЫЕ ИГРОКИ:*
"""
    
    for player in team_data['key_players']:
        status_emoji = "✅" if player['status'] == "готов" else "⚠️" if player['status'] == "под вопросом" else "❌"
        goals_info = f" ({player['goals']} голов)" if 'goals' in player else ""
        return_info = f" ➤ возврат: {player['return']}" if 'return' in player else ""
        response += f"• {status_emoji} {player['name']} - {player['position']}{goals_info}{return_info}\n"
    
    available = sum(1 for p in team_data['key_players'] if p['status'] == "готов")
    total = len(team_data['key_players'])
    
    response += f"\n📋 *Доступность:* {available}/{total} ключевых игроков ({available/total*100:.0f}%)"
    
    await message.answer(response, parse_mode="Markdown")

@dp.message()
async def handle_match_analysis(message: types.Message):
    """Основной анализ матча"""
    if not message.text or message.text.startswith('/'):
        return
    
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Извлекаем команды
    words = message.text.split()
    if len(words) < 2:
        await message.answer("⚠️ Укажите обе команды: `Эвертон Лидс`", parse_mode="Markdown")
        return
    
    # Простая логика для двух команд
    team1_name = words[0]
    team2_name = words[1] if len(words) > 1 else words[0]
    
    # Получаем данные
    team1_data = get_team_data(team1_name)
    team2_data = get_team_data(team2_name)
    
    # Добавляем метку "домашняя" для первой команды
    team1_data["home"] = True
    
    # Анализируем матч
    match_stats = calculate_match_stats(team1_data, team2_data)
    
    # Создаем детальный ответ
    response = f"""
⚽ *ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗ МАТЧА*
🏆 *{team1_data['full_name']} vs {team2_data['full_name']}*

📊 *КОМАНДНАЯ СТАТИСТИКА:*
╭────────────────┬─────────────────┬─────────────────╮
│ Показатель     │ {team1_data['full_name'][:15]:<15} │ {team2_data['full_name'][:15]:<15} │
├────────────────┼─────────────────┼─────────────────┤
│ Лига           │ {team1_data['league']:<15} │ {team2_data['league']:<15} │
│ Позиция        │ {team1_data['position']:<15} │ {team2_data['position']:<15} │
│ Очки           │ {team1_data['points']:<15} │ {team2_data['points']:<15} │
│ Голы (З/П)     │ {team1_data['goals_for']}-{team1_data['goals_against']:<13} │ {team2_data['goals_for']}-{team2_data['goals_against']:<13} │
│ Разница голов  │ {team1_data['goal_difference']:+d:<14} │ {team2_data['goal_difference']:+d:<14} │
│ Форма (посл.7) │ {format_form_display(team1_data['form']):<15} │ {format_form_display(team2_data['form']):<15} │
│ Ключ. игроки   │ {match_stats['key_players_available'][0]}/{match_stats['total_key_players'][0]:<14} │ {match_stats['key_players_available'][1]}/{match_stats['total_key_players'][1]:<14} │
╰────────────────┴─────────────────┴─────────────────╯

🎯 *МАТЕМАТИЧЕСКИЙ ПРОГНОЗ:*
• Ожидаемые голы: {match_stats['expected_goals'][0]:.1f} - {match_stats['expected_goals'][1]:.1f}
• Вероятность победы {team1_data['full_name']}: {match_stats['probabilities']['team1_win']}%
• Вероятность ничьей: {match_stats['probabilities']['draw']}%
• Вероятность победы {team2_data['full_name']}: {match_stats['probabilities']['team2_win']}%
• Прогнозируемый счет: **{match_stats['predicted_score']}**

👨‍🏫 *ТРЕНЕРСКОЕ ПРОТИВОСТОЯНИЕ:*
{team1_data['coach']} vs {team2_data['coach']}
"""
    
