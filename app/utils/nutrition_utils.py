from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random


class NutritionCalculator:
	"""Калькулятор питания"""
	
	@staticmethod
	def calculate_bmr(weight_kg: float, height_cm: int, age: int, gender: str) -> float:
		"""
		Рассчитать базовый метаболизм (BMR) по формуле Миффлина-Сан Жеора
		
		Args:
			weight_kg: Вес в кг
			height_cm: Рост в см
			age: Возраст
			gender: Пол ('male' или 'female')
		
		Returns:
			float: BMR в ккал
		"""
		if gender.lower() == 'male':
			bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
		else:
			bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
		
		return bmr
	
	@staticmethod
	def calculate_tdee(bmr: float, activity_level: str) -> float:
		"""
		Рассчитать общий расход энергии (TDEE)
		
		Args:
			bmr: Базовый метаболизм
			activity_level: Уровень активности
		
		Returns:
			float: TDEE в ккал
		"""
		activity_multipliers = {
			'sedentary': 1.2,      # Сидячий образ жизни
			'light': 1.375,        # Легкая активность
			'moderate': 1.55,      # Умеренная активность
			'active': 1.725,       # Высокая активность
			'very_active': 1.9     # Очень высокая активность
		}
		
		multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
		return bmr * multiplier
	
	@staticmethod
	def calculate_macros_for_goal(
		tdee: float, 
		goal: str, 
		weight_kg: float
	) -> Dict[str, float]:
		"""
		Рассчитать макронутриенты для цели
		
		Args:
			tdee: Общий расход энергии
			goal: Цель ('lose_weight', 'gain_mass', 'cut', 'tone')
			weight_kg: Вес в кг
		
		Returns:
			Dict с калориями и макронутриентами
		"""
		# Корректируем калории под цель
		if goal == 'lose_weight':
			calories = tdee - 500  # Дефицит 500 ккал
		elif goal == 'gain_mass':
			calories = tdee + 300  # Профицит 300 ккал
		elif goal == 'cut':
			calories = tdee - 300  # Небольшой дефицит
		else:  # tone
			calories = tdee  # Поддержание веса
		
		# Рассчитываем белки (1.6-2.2 г на кг веса)
		protein_g = weight_kg * 2.0
		
		# Рассчитываем жиры (20-35% от калорий)
		fat_calories = calories * 0.25
		fat_g = fat_calories / 9
		
		# Оставшиеся калории идут на углеводы
		remaining_calories = calories - (protein_g * 4) - (fat_g * 9)
		carbs_g = remaining_calories / 4
		
		return {
			'calories': round(calories),
			'protein_g': round(protein_g, 1),
			'fat_g': round(fat_g, 1),
			'carbs_g': round(carbs_g, 1)
		}


class MealPlanner:
	"""Планировщик питания"""
	
	def __init__(self):
		self.meal_database = self._load_meal_database()
	
	def _load_meal_database(self) -> Dict[str, List[Dict]]:
		"""Загрузить базу блюд"""
		return {
			'breakfast': [
				{
					'name': 'Овсянка с ягодами',
					'calories': 320,
					'protein': 12,
					'fat': 8,
					'carbs': 52,
					'recipe': '1. Сварить овсянку на воде\n2. Добавить ягоды\n3. Посыпать орехами',
					'tags': ['веган', 'быстро']
				},
				{
					'name': 'Творожная запеканка',
					'calories': 280,
					'protein': 18,
					'fat': 12,
					'carbs': 25,
					'recipe': '1. Смешать творог с яйцами\n2. Добавить мед\n3. Запечь в духовке',
					'tags': ['белок', 'сладкое']
				},
				{
					'name': 'Смузи с протеином',
					'calories': 250,
					'protein': 25,
					'fat': 5,
					'carbs': 30,
					'recipe': '1. Смешать банан, ягоды, протеин\n2. Добавить молоко\n3. Взбить в блендере',
					'tags': ['протеин', 'быстро']
				}
			],
			'lunch': [
				{
					'name': 'Куриная грудка с овощами',
					'calories': 350,
					'protein': 35,
					'fat': 8,
					'carbs': 25,
					'recipe': '1. Запечь куриную грудку\n2. Приготовить овощи на пару\n3. Подать с рисом',
					'tags': ['белок', 'овощи']
				},
				{
					'name': 'Лосось с киноа',
					'calories': 420,
					'protein': 28,
					'fat': 22,
					'carbs': 35,
					'recipe': '1. Запечь лосось\n2. Сварить киноа\n3. Добавить овощи',
					'tags': ['омега-3', 'белок']
				},
				{
					'name': 'Салат с тунцом',
					'calories': 280,
					'protein': 25,
					'fat': 12,
					'carbs': 15,
					'recipe': '1. Смешать листья салата\n2. Добавить тунец\n3. Заправить оливковым маслом',
					'tags': ['белок', 'легкий']
				}
			],
			'dinner': [
				{
					'name': 'Индейка с гречкой',
					'calories': 380,
					'protein': 32,
					'fat': 10,
					'carbs': 40,
					'recipe': '1. Запечь индейку\n2. Сварить гречку\n3. Подать с овощами',
					'tags': ['белок', 'медленные углеводы']
				},
				{
					'name': 'Творог с фруктами',
					'calories': 220,
					'protein': 20,
					'fat': 8,
					'carbs': 18,
					'recipe': '1. Смешать творог с фруктами\n2. Добавить мед\n3. Посыпать орехами',
					'tags': ['белок', 'легкий']
				},
				{
					'name': 'Омлет с овощами',
					'calories': 280,
					'protein': 18,
					'fat': 15,
					'carbs': 12,
					'recipe': '1. Взбить яйца\n2. Добавить овощи\n3. Запечь на сковороде',
					'tags': ['белок', 'быстро']
				}
			],
			'snack': [
				{
					'name': 'Протеиновый коктейль',
					'calories': 180,
					'protein': 25,
					'fat': 3,
					'carbs': 15,
					'recipe': '1. Смешать протеин с водой\n2. Добавить банан\n3. Взбить',
					'tags': ['протеин', 'быстро']
				},
				{
					'name': 'Орехи и сухофрукты',
					'calories': 200,
					'protein': 6,
					'fat': 12,
					'carbs': 20,
					'recipe': '1. Смешать орехи\n2. Добавить сухофрукты\n3. Разделить на порции',
					'tags': ['здоровые жиры', 'энергия']
				},
				{
					'name': 'Йогурт с ягодами',
					'calories': 150,
					'protein': 12,
					'fat': 5,
					'carbs': 18,
					'recipe': '1. Смешать йогурт с ягодами\n2. Добавить мед\n3. Посыпать орехами',
					'tags': ['белок', 'кальций']
				}
			]
		}
	
	def generate_weekly_meal_plan(
		self, 
		target_calories: int,
		target_protein: float,
		target_fat: float,
		target_carbs: float,
		preferences: Optional[List[str]] = None
	) -> Dict[str, List[Dict]]:
		"""
		Сгенерировать план питания на неделю
		
		Args:
			target_calories: Целевые калории
			target_protein: Целевой белок в граммах
			target_fat: Целевой жир в граммах
			target_carbs: Целевые углеводы в граммах
			preferences: Предпочтения (например, ['веган', 'без глютена'])
		
		Returns:
			Dict с планом питания на неделю
		"""
		plan = {}
		days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
		
		for day in days:
			plan[day] = {
				'breakfast': self._select_meal('breakfast', target_calories * 0.25, preferences),
				'lunch': self._select_meal('lunch', target_calories * 0.35, preferences),
				'dinner': self._select_meal('dinner', target_calories * 0.30, preferences),
				'snack': self._select_meal('snack', target_calories * 0.10, preferences)
			}
		
		return plan
	
	def _select_meal(
		self, 
		meal_type: str, 
		target_calories: float, 
		preferences: Optional[List[str]] = None
	) -> Dict:
		"""Выбрать блюдо для приема пищи"""
		available_meals = self.meal_database[meal_type]
		
		# Фильтруем по предпочтениям
		if preferences:
			filtered_meals = []
			for meal in available_meals:
				if any(pref in meal.get('tags', []) for pref in preferences):
					filtered_meals.append(meal)
			
			if filtered_meals:
				available_meals = filtered_meals
		
		# Выбираем случайное блюдо
		selected_meal = random.choice(available_meals)
		
		# Корректируем порцию под целевые калории
		calorie_ratio = target_calories / selected_meal['calories']
		
		return {
			'name': selected_meal['name'],
			'calories': round(selected_meal['calories'] * calorie_ratio),
			'protein': round(selected_meal['protein'] * calorie_ratio, 1),
			'fat': round(selected_meal['fat'] * calorie_ratio, 1),
			'carbs': round(selected_meal['carbs'] * calorie_ratio, 1),
			'recipe': selected_meal['recipe'],
			'tags': selected_meal.get('tags', [])
		}
	
	def search_meals(
		self, 
		query: str, 
		meal_type: Optional[str] = None,
		max_calories: Optional[int] = None
	) -> List[Dict]:
		"""
		Поиск блюд
		
		Args:
			query: Поисковый запрос
			meal_type: Тип приема пищи
			max_calories: Максимальные калории
		
		Returns:
			List с найденными блюдами
		"""
		results = []
		query_lower = query.lower()
		
		meal_types = [meal_type] if meal_type else self.meal_database.keys()
		
		for mt in meal_types:
			if mt in self.meal_database:
				for meal in self.meal_database[mt]:
					# Проверяем название
					if query_lower in meal['name'].lower():
						if max_calories is None or meal['calories'] <= max_calories:
							meal_copy = meal.copy()
							meal_copy['meal_type'] = mt
							results.append(meal_copy)
					
					# Проверяем теги
					elif any(query_lower in tag.lower() for tag in meal.get('tags', [])):
						if max_calories is None or meal['calories'] <= max_calories:
							meal_copy = meal.copy()
							meal_copy['meal_type'] = mt
							results.append(meal_copy)
		
		return results


class NutritionAnalyzer:
	"""Анализатор питания"""
	
	@staticmethod
	def analyze_meal_photo(photo_description: str) -> Dict[str, float]:
		"""
		Анализировать фото блюда (заглушка для AI)
		
		Args:
			photo_description: Описание блюда
		
		Returns:
			Dict с примерными КБЖУ
		"""
		# В реальном проекте здесь должна быть интеграция с Google Vision API
		# Пока что возвращаем примерные значения
		
		description_lower = photo_description.lower()
		
		# Простая логика определения блюда
		if 'курица' in description_lower or 'грудка' in description_lower:
			return {'calories': 250, 'protein': 30, 'fat': 8, 'carbs': 15}
		elif 'рыба' in description_lower or 'лосось' in description_lower:
			return {'calories': 280, 'protein': 25, 'fat': 15, 'carbs': 10}
		elif 'овощи' in description_lower or 'салат' in description_lower:
			return {'calories': 120, 'protein': 8, 'fat': 5, 'carbs': 15}
		elif 'каша' in description_lower or 'овсянка' in description_lower:
			return {'calories': 200, 'protein': 8, 'fat': 5, 'carbs': 35}
		elif 'творог' in description_lower:
			return {'calories': 180, 'protein': 20, 'fat': 8, 'carbs': 10}
		else:
			# Средние значения для неизвестного блюда
			return {'calories': 200, 'protein': 15, 'fat': 10, 'carbs': 20}
	
	@staticmethod
	def get_nutrition_advice(goal: str, current_weight: float, target_weight: float) -> str:
		"""
		Получить совет по питанию
		
		Args:
			goal: Цель
			current_weight: Текущий вес
			target_weight: Целевой вес
		
		Returns:
			str: Совет по питанию
		"""
		weight_diff = target_weight - current_weight
		
		if goal == 'lose_weight':
			if weight_diff < -5:
				return "Отличный прогресс! Продолжайте придерживаться дефицита калорий и не забывайте про белок."
			elif weight_diff < -2:
				return "Хороший результат! Увеличьте потребление белка для сохранения мышечной массы."
			else:
				return "Начните с дефицита 500 ккал в день. Увеличьте потребление белка до 2г на кг веса."
		
		elif goal == 'gain_mass':
			if weight_diff > 5:
				return "Отличный прогресс! Увеличьте калории еще на 200-300 ккал для дальнейшего роста."
			elif weight_diff > 2:
				return "Хороший результат! Продолжайте профицит калорий и тренировки."
			else:
				return "Начните с профицита 300 ккал в день. Увеличьте потребление белка до 2.2г на кг веса."
		
		elif goal == 'cut':
			return "Сфокусируйтесь на сохранении мышечной массы. Потребляйте 2г белка на кг веса."
		
		else:  # tone
			return "Поддерживайте текущий вес. Сбалансируйте питание и регулярно тренируйтесь."
	
	@staticmethod
	def calculate_water_intake(weight_kg: float, activity_level: str) -> float:
		"""
		Рассчитать рекомендуемое потребление воды
		
		Args:
			weight_kg: Вес в кг
			activity_level: Уровень активности
		
		Returns:
			float: Рекомендуемое потребление воды в литрах
		"""
		base_water = weight_kg * 0.033  # 33мл на кг веса
		
		activity_multipliers = {
			'sedentary': 1.0,
			'light': 1.1,
			'moderate': 1.2,
			'active': 1.3,
			'very_active': 1.4
		}
		
		multiplier = activity_multipliers.get(activity_level.lower(), 1.0)
		return round(base_water * multiplier, 1)


# Глобальные экземпляры
nutrition_calculator = NutritionCalculator()
meal_planner = MealPlanner()
nutrition_analyzer = NutritionAnalyzer()