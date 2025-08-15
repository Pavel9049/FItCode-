from datetime import datetime, timedelta
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# Полная база ПП-блюд
MEALS_DATABASE = {
	"breakfast": [
		{"title": "Овсянка с ягодами", "kcal": 320, "proteins": 12, "fats": 8, "carbs": 52, "tags": "breakfast", "recipe": "1. Сварить овсянку на воде\n2. Добавить ягоды\n3. Посыпать орехами", "photo_url": "https://example.com/oatmeal.jpg"},
		{"title": "Творожная запеканка", "kcal": 280, "proteins": 18, "fats": 12, "carbs": 25, "tags": "breakfast", "recipe": "1. Смешать творог с яйцами\n2. Добавить мед\n3. Запечь в духовке", "photo_url": "https://example.com/cottage_cheese.jpg"},
		{"title": "Смузи с протеином", "kcal": 250, "proteins": 25, "fats": 5, "carbs": 30, "tags": "breakfast", "recipe": "1. Смешать банан, ягоды, протеин\n2. Добавить молоко\n3. Взбить в блендере", "photo_url": "https://example.com/smoothie.jpg"},
		{"title": "Яичница с овощами", "kcal": 300, "proteins": 20, "fats": 15, "carbs": 15, "tags": "breakfast", "recipe": "1. Обжарить овощи\n2. Добавить яйца\n3. Посолить и поперчить", "photo_url": "https://example.com/eggs.jpg"},
		{"title": "Гречка с молоком", "kcal": 280, "proteins": 10, "fats": 8, "carbs": 45, "tags": "breakfast", "recipe": "1. Сварить гречку\n2. Добавить молоко\n3. Добавить мед", "photo_url": "https://example.com/buckwheat.jpg"},
		{"title": "Тост с авокадо", "kcal": 220, "proteins": 8, "fats": 12, "carbs": 25, "tags": "breakfast", "recipe": "1. Поджарить хлеб\n2. Размять авокадо\n3. Намазать на тост", "photo_url": "https://example.com/avocado_toast.jpg"},
		{"title": "Йогурт с гранолой", "kcal": 200, "proteins": 15, "fats": 8, "carbs": 22, "tags": "breakfast", "recipe": "1. Смешать йогурт с гранолой\n2. Добавить мед\n3. Посыпать орехами", "photo_url": "https://example.com/yogurt.jpg"},
		{"title": "Блины из овсянки", "kcal": 180, "proteins": 12, "fats": 6, "carbs": 28, "tags": "breakfast", "recipe": "1. Смешать овсянку с яйцами\n2. Добавить молоко\n3. Жарить на сковороде", "photo_url": "https://example.com/oatmeal_pancakes.jpg"},
		{"title": "Сырники", "kcal": 260, "proteins": 16, "fats": 10, "carbs": 30, "tags": "breakfast", "recipe": "1. Смешать творог с яйцами\n2. Добавить муку\n3. Жарить на сковороде", "photo_url": "https://example.com/cheesecakes.jpg"},
		{"title": "Каша из киноа", "kcal": 240, "proteins": 14, "fats": 8, "carbs": 35, "tags": "breakfast", "recipe": "1. Сварить киноа\n2. Добавить фрукты\n3. Посыпать орехами", "photo_url": "https://example.com/quinoa.jpg"},
		{"title": "Омлет с сыром", "kcal": 320, "proteins": 22, "fats": 18, "carbs": 8, "tags": "breakfast", "recipe": "1. Взбить яйца\n2. Добавить сыр\n3. Запечь на сковороде", "photo_url": "https://example.com/omelette.jpg"},
		{"title": "Мюсли с молоком", "kcal": 200, "proteins": 10, "fats": 6, "carbs": 32, "tags": "breakfast", "recipe": "1. Залить мюсли молоком\n2. Добавить фрукты\n3. Дать настояться", "photo_url": "https://example.com/muesli.jpg"}
	],
	"lunch": [
		{"title": "Куриная грудка с овощами", "kcal": 350, "proteins": 35, "fats": 8, "carbs": 25, "tags": "lunch", "recipe": "1. Запечь куриную грудку\n2. Приготовить овощи на пару\n3. Подать с рисом", "photo_url": "https://example.com/chicken_breast.jpg"},
		{"title": "Лосось с киноа", "kcal": 420, "proteins": 28, "fats": 22, "carbs": 35, "tags": "lunch", "recipe": "1. Запечь лосось\n2. Сварить киноа\n3. Добавить овощи", "photo_url": "https://example.com/salmon.jpg"},
		{"title": "Салат с тунцом", "kcal": 280, "proteins": 25, "fats": 12, "carbs": 15, "tags": "lunch", "recipe": "1. Смешать листья салата\n2. Добавить тунец\n3. Заправить оливковым маслом", "photo_url": "https://example.com/tuna_salad.jpg"},
		{"title": "Индейка с гречкой", "kcal": 380, "proteins": 32, "fats": 10, "carbs": 40, "tags": "lunch", "recipe": "1. Запечь индейку\n2. Сварить гречку\n3. Подать с овощами", "photo_url": "https://example.com/turkey.jpg"},
		{"title": "Суп из чечевицы", "kcal": 250, "proteins": 18, "fats": 6, "carbs": 35, "tags": "lunch", "recipe": "1. Сварить чечевицу\n2. Добавить овощи\n3. Приправить специями", "photo_url": "https://example.com/lentil_soup.jpg"},
		{"title": "Стейк из говядины", "kcal": 450, "proteins": 40, "fats": 25, "carbs": 8, "tags": "lunch", "recipe": "1. Обжарить стейк\n2. Подать с овощами\n3. Добавить соус", "photo_url": "https://example.com/beef_steak.jpg"},
		{"title": "Паста с креветками", "kcal": 380, "proteins": 22, "fats": 12, "carbs": 45, "tags": "lunch", "recipe": "1. Сварить пасту\n2. Обжарить креветки\n3. Смешать с соусом", "photo_url": "https://example.com/shrimp_pasta.jpg"},
		{"title": "Котлеты из индейки", "kcal": 320, "proteins": 28, "fats": 15, "carbs": 20, "tags": "lunch", "recipe": "1. Смешать фарш с овощами\n2. Сформировать котлеты\n3. Запечь в духовке", "photo_url": "https://example.com/turkey_patties.jpg"},
		{"title": "Салат Цезарь", "kcal": 300, "proteins": 20, "fats": 18, "carbs": 15, "tags": "lunch", "recipe": "1. Смешать салат\n2. Добавить курицу\n3. Заправить соусом", "photo_url": "https://example.com/caesar_salad.jpg"},
		{"title": "Рыба на пару", "kcal": 280, "proteins": 30, "fats": 8, "carbs": 12, "tags": "lunch", "recipe": "1. Приготовить рыбу на пару\n2. Подать с овощами\n3. Добавить лимон", "photo_url": "https://example.com/steamed_fish.jpg"},
		{"title": "Бургер из индейки", "kcal": 350, "proteins": 25, "fats": 15, "carbs": 30, "tags": "lunch", "recipe": "1. Сформировать котлету\n2. Обжарить\n3. Собрать бургер", "photo_url": "https://example.com/turkey_burger.jpg"},
		{"title": "Куриный суп", "kcal": 200, "proteins": 18, "fats": 6, "carbs": 20, "tags": "lunch", "recipe": "1. Сварить куриный бульон\n2. Добавить овощи\n3. Добавить курицу", "photo_url": "https://example.com/chicken_soup.jpg"}
	],
	"dinner": [
		{"title": "Творог с фруктами", "kcal": 220, "proteins": 20, "fats": 8, "carbs": 18, "tags": "dinner", "recipe": "1. Смешать творог с фруктами\n2. Добавить мед\n3. Посыпать орехами", "photo_url": "https://example.com/cottage_fruits.jpg"},
		{"title": "Омлет с овощами", "kcal": 280, "proteins": 18, "fats": 15, "carbs": 12, "tags": "dinner", "recipe": "1. Взбить яйца\n2. Добавить овощи\n3. Запечь на сковороде", "photo_url": "https://example.com/vegetable_omelette.jpg"},
		{"title": "Салат с авокадо", "kcal": 250, "proteins": 12, "fats": 18, "carbs": 15, "tags": "dinner", "recipe": "1. Смешать овощи\n2. Добавить авокадо\n3. Заправить маслом", "photo_url": "https://example.com/avocado_salad.jpg"},
		{"title": "Куриная грудка с салатом", "kcal": 300, "proteins": 35, "fats": 10, "carbs": 15, "tags": "dinner", "recipe": "1. Запечь куриную грудку\n2. Приготовить салат\n3. Подать вместе", "photo_url": "https://example.com/chicken_salad.jpg"},
		{"title": "Рыба с овощами", "kcal": 280, "proteins": 28, "fats": 12, "carbs": 18, "tags": "dinner", "recipe": "1. Запечь рыбу\n2. Приготовить овощи\n3. Подать вместе", "photo_url": "https://example.com/fish_vegetables.jpg"},
		{"title": "Творожная запеканка", "kcal": 260, "proteins": 18, "fats": 10, "carbs": 25, "tags": "dinner", "recipe": "1. Смешать творог с яйцами\n2. Добавить фрукты\n3. Запечь", "photo_url": "https://example.com/cottage_casserole.jpg"},
		{"title": "Овощной суп", "kcal": 180, "proteins": 8, "fats": 6, "carbs": 25, "tags": "dinner", "recipe": "1. Сварить овощной бульон\n2. Добавить овощи\n3. Приправить специями", "photo_url": "https://example.com/vegetable_soup.jpg"},
		{"title": "Салат с тунцом", "kcal": 220, "proteins": 20, "fats": 10, "carbs": 12, "tags": "dinner", "recipe": "1. Смешать овощи\n2. Добавить тунец\n3. Заправить маслом", "photo_url": "https://example.com/tuna_dinner.jpg"},
		{"title": "Куриные котлеты", "kcal": 280, "proteins": 25, "fats": 12, "carbs": 20, "tags": "dinner", "recipe": "1. Сформировать котлеты\n2. Запечь в духовке\n3. Подать с овощами", "photo_url": "https://example.com/chicken_patties.jpg"},
		{"title": "Творог с медом", "kcal": 200, "proteins": 18, "fats": 8, "carbs": 15, "tags": "dinner", "recipe": "1. Смешать творог с медом\n2. Добавить орехи\n3. Подать", "photo_url": "https://example.com/cottage_honey.jpg"},
		{"title": "Овощной омлет", "kcal": 240, "proteins": 16, "fats": 12, "carbs": 15, "tags": "dinner", "recipe": "1. Взбить яйца\n2. Добавить овощи\n3. Запечь", "photo_url": "https://example.com/vegetable_omelette_dinner.jpg"},
		{"title": "Салат с курицей", "kcal": 260, "proteins": 22, "fats": 12, "carbs": 18, "tags": "dinner", "recipe": "1. Смешать овощи\n2. Добавить курицу\n3. Заправить соусом", "photo_url": "https://example.com/chicken_salad_dinner.jpg"}
	],
	"snack": [
		{"title": "Протеиновый коктейль", "kcal": 180, "proteins": 25, "fats": 3, "carbs": 15, "tags": "snack", "recipe": "1. Смешать протеин с водой\n2. Добавить банан\n3. Взбить", "photo_url": "https://example.com/protein_shake.jpg"},
		{"title": "Орехи и сухофрукты", "kcal": 200, "proteins": 6, "fats": 12, "carbs": 20, "tags": "snack", "recipe": "1. Смешать орехи\n2. Добавить сухофрукты\n3. Разделить на порции", "photo_url": "https://example.com/nuts_dried_fruits.jpg"},
		{"title": "Йогурт с ягодами", "kcal": 150, "proteins": 12, "fats": 5, "carbs": 18, "tags": "snack", "recipe": "1. Смешать йогурт с ягодами\n2. Добавить мед\n3. Посыпать орехами", "photo_url": "https://example.com/yogurt_berries.jpg"},
		{"title": "Яблоко с ореховой пастой", "kcal": 180, "proteins": 4, "fats": 8, "carbs": 25, "tags": "snack", "recipe": "1. Нарезать яблоко\n2. Намазать ореховую пасту\n3. Подать", "photo_url": "https://example.com/apple_nut_butter.jpg"},
		{"title": "Творог с фруктами", "kcal": 160, "proteins": 15, "fats": 6, "carbs": 15, "tags": "snack", "recipe": "1. Смешать творог с фруктами\n2. Добавить мед\n3. Подать", "photo_url": "https://example.com/cottage_fruits_snack.jpg"},
		{"title": "Смузи с овощами", "kcal": 120, "proteins": 8, "fats": 4, "carbs": 18, "tags": "snack", "recipe": "1. Смешать овощи с фруктами\n2. Добавить воду\n3. Взбить в блендере", "photo_url": "https://example.com/vegetable_smoothie.jpg"},
		{"title": "Батончик с орехами", "kcal": 220, "proteins": 8, "fats": 12, "carbs": 25, "tags": "snack", "recipe": "1. Смешать орехи с медом\n2. Добавить сухофрукты\n3. Сформировать батончик", "photo_url": "https://example.com/nut_bar.jpg"},
		{"title": "Кефир с отрубями", "kcal": 140, "proteins": 10, "fats": 5, "carbs": 15, "tags": "snack", "recipe": "1. Смешать кефир с отрубями\n2. Добавить мед\n3. Подать", "photo_url": "https://example.com/kefir_bran.jpg"},
		{"title": "Салат из фруктов", "kcal": 160, "proteins": 4, "fats": 2, "carbs": 35, "tags": "snack", "recipe": "1. Нарезать фрукты\n2. Смешать\n3. Подать", "photo_url": "https://example.com/fruit_salad.jpg"},
		{"title": "Творожная масса", "kcal": 180, "proteins": 16, "fats": 8, "carbs": 12, "tags": "snack", "recipe": "1. Смешать творог с медом\n2. Добавить ваниль\n3. Подать", "photo_url": "https://example.com/cottage_mass.jpg"},
		{"title": "Ореховое молоко", "kcal": 120, "proteins": 4, "fats": 8, "carbs": 10, "tags": "snack", "recipe": "1. Смешать орехи с водой\n2. Взбить в блендере\n3. Процедить", "photo_url": "https://example.com/nut_milk.jpg"},
		{"title": "Семена чиа с йогуртом", "kcal": 140, "proteins": 8, "fats": 6, "carbs": 15, "tags": "snack", "recipe": "1. Смешать семена чиа с йогуртом\n2. Добавить мед\n3. Дать настояться", "photo_url": "https://example.com/chia_yogurt.jpg"}
	]
}

SAMPLE_MEALS = [
	{"title": "Овсянка с ягодами", "kcal": 320, "proteins": 12, "fats": 8, "carbs": 52, "tags": "breakfast"},
	{"title": "Курица с рисом", "kcal": 450, "proteins": 35, "fats": 10, "carbs": 55, "tags": "lunch"},
	{"title": "Лосось и киноа", "kcal": 520, "proteins": 40, "fats": 20, "carbs": 45, "tags": "dinner"},
	{"title": "Творог с орехами", "kcal": 280, "proteins": 22, "fats": 12, "carbs": 20, "tags": "snack"},
]


def generate_week_menu() -> Dict:
	week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
	days: Dict[str, List[Dict]] = {}
	for i in range(7):
		day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
		days[day] = SAMPLE_MEALS
	return {"week_start": week_start.isoformat(), "days": days}


def get_meals_by_type(meal_type: str) -> List[Dict]:
	"""Получить блюда по типу приема пищи"""
	return MEALS_DATABASE.get(meal_type, [])


def search_meals(query: str, meal_type: str = None) -> List[Dict]:
	"""Поиск блюд по запросу"""
	results = []
	query = query.lower()
	
	for meal_type_key, meals in MEALS_DATABASE.items():
		if meal_type and meal_type_key != meal_type:
			continue
		for meal in meals:
			if query in meal["title"].lower():
				results.append(meal)
	
	return results


def get_meals_by_calories(max_calories: int, meal_type: str = None) -> List[Dict]:
	"""Получить блюда с ограничением по калориям"""
	results = []
	
	for meal_type_key, meals in MEALS_DATABASE.items():
		if meal_type and meal_type_key != meal_type:
			continue
		for meal in meals:
			if meal["kcal"] <= max_calories:
				results.append(meal)
	
	return results


def generate_personal_meal_plan(target_calories: int, target_proteins: float, target_fats: float, target_carbs: float) -> Dict:
	"""Генерировать персональный план питания"""
	plan = {
		"breakfast": [],
		"lunch": [],
		"dinner": [],
		"snack": []
	}
	
	# Распределяем калории по приемам пищи
	breakfast_calories = int(target_calories * 0.25)
	lunch_calories = int(target_calories * 0.35)
	dinner_calories = int(target_calories * 0.30)
	snack_calories = int(target_calories * 0.10)
	
	# Подбираем блюда для каждого приема пищи
	plan["breakfast"] = get_meals_by_calories(breakfast_calories, "breakfast")[:3]
	plan["lunch"] = get_meals_by_calories(lunch_calories, "lunch")[:3]
	plan["dinner"] = get_meals_by_calories(dinner_calories, "dinner")[:3]
	plan["snack"] = get_meals_by_calories(snack_calories, "snack")[:2]
	
	return plan


def render_menu_pdf(menu: Dict) -> bytes:
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=A4)
	width, height = A4
	y = height - 50
	c.setFont("Helvetica-Bold", 16)
	c.drawString(50, y, "Меню на неделю")
	y -= 30
	c.setFont("Helvetica", 11)
	for day, meals in menu["days"].items():
		c.drawString(50, y, day)
		y -= 20
		for m in meals:
			line = f"- {m['title']} — {m['kcal']} ккал / {m['proteins']}Б/{m['fats']}Ж/{m['carbs']}У"
			c.drawString(70, y, line)
			y -= 16
			if y < 80:
				c.showPage()
				y = height - 50
	c.showPage()
	c.save()
	buf.seek(0)
	return buf.read()