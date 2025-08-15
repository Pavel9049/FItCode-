from datetime import datetime, timedelta
from typing import Dict, List
from app.db.models import ProgramLevel
import json


SPLITS = [
	{"day": "Push", "groups": ["chest", "shoulders", "triceps"]},
	{"day": "Pull", "groups": ["back", "biceps", "forearms"]},
	{"day": "Legs", "groups": ["legs", "abs", "calves"]},
	{"day": "Upper", "groups": ["back", "chest", "shoulders"]},
	{"day": "Lower", "groups": ["legs", "abs", "glutes"]},
]

BODYWEIGHT_EX = {
	"beginner": ["Приседания", "Отжимания от стены", "Планка 20с"],
	"novice": ["Отжимания", "Выпады", "Планка 30с"],
	"advanced": ["Отжимания + хлопок", "Пистолетики", "Планка 45с"],
	"pro": ["Отжимания в стойке у стены", "Прыжковые приседания", "Планка 60с"],
}


def estimate_working_weight(weight_kg: float | None, level: ProgramLevel | None) -> int:
	if not weight_kg:
		return 10
	factor = {ProgramLevel.beginner: 0.2, ProgramLevel.novice: 0.3, ProgramLevel.advanced: 0.4, ProgramLevel.pro: 0.5}.get(level or ProgramLevel.beginner, 0.25)
	return max(5, int(weight_kg * factor))


def generate_week_plan(level: ProgramLevel, goal: str, weight_kg: float | None, has_equipment: bool) -> Dict:
	week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
	plan: Dict[str, List[Dict]] = {}
	if not has_equipment:
		# Домашние тренировки без инвентаря
		ex_list = BODYWEIGHT_EX[level.value]
		for i in range(7):
			day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
			plan[day] = [{"name": n, "sets": 3, "reps": 12} for n in ex_list]
		return {"type": "bodyweight", "goal": goal, "level": level.value, "week_start": week_start.isoformat(), "days": plan}
	else:
		# Сплит PPL/Upper/Lower
		for i in range(5):
			day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
			split = SPLITS[i]
			entries = []
			for g in split["groups"]:
				entries.append({
					"group": g,
					"exercises": [
						{"name": f"Упражнение на {g} #1", "sets": 4, "reps": 10, "weight": estimate_working_weight(weight_kg, level)},
						{"name": f"Упражнение на {g} #2", "sets": 3, "reps": 12, "weight": estimate_working_weight(weight_kg, level)},
						{"name": f"Упражнение на {g} #3", "sets": 3, "reps": 15, "weight": estimate_working_weight(weight_kg, level)},
					]
				})
			plan[day] = entries
		return {"type": "split", "goal": goal, "level": level.value, "week_start": week_start.isoformat(), "days": plan}