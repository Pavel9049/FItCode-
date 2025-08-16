from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random
from enum import Enum

class NutritionGoal(Enum):
    LOSE_WEIGHT = "lose_weight"
    GAIN_MASS = "gain_mass"
    CUT = "cut"
    TONE = "tone"

class MealType(Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class Meal:
    def __init__(
        self,
        name: str,
        meal_type: MealType,
        calories: int,
        protein: float,
        fat: float,
        carbs: float,
        recipe: str,
        image_url: str,
        video_url: str,
        ingredients: List[str],
        cooking_time: int,  # в минутах
        difficulty: int,  # 1-5
        tags: List[str],
        nutrition_notes: str = ""
    ):
        self.name = name
        self.meal_type = meal_type
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
        self.recipe = recipe
        self.image_url = image_url
        self.video_url = video_url
        self.ingredients = ingredients
        self.cooking_time = cooking_time
        self.difficulty = difficulty
        self.tags = tags
        self.nutrition_notes = nutrition_notes

class NutritionCalculator:
    """Калькулятор питания"""

    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: int, age: int, gender: str) -> float:
        """Рассчитать базовый метаболизм (BMR) по формуле Миффлина-Сан Жеора"""
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return bmr

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """Рассчитать общий расход энергии (TDEE)"""
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
        goal: NutritionGoal,
        weight_kg: float,
        activity_level: str = "moderate"
    ) -> Dict[str, float]:
        """Рассчитать макронутриенты для цели"""
        
        # Корректировка калорий в зависимости от цели
        if goal == NutritionGoal.LOSE_WEIGHT:
            calories = tdee - 500  # Дефицит 500 ккал
        elif goal == NutritionGoal.GAIN_MASS:
            calories = tdee + 300  # Профицит 300 ккал
        elif goal == NutritionGoal.CUT:
            calories = tdee - 300  # Дефицит 300 ккал
        else:  # TONE
            calories = tdee
        
        # Расчет белков (в зависимости от цели)
        if goal == NutritionGoal.GAIN_MASS:
            protein_g = weight_kg * 2.2  # Больше белка для роста мышц
        elif goal == NutritionGoal.LOSE_WEIGHT:
            protein_g = weight_kg * 2.0  # Высокий белок для сохранения мышц
        else:
            protein_g = weight_kg * 1.8  # Стандартное количество
        
        # Расчет жиров
        if goal == NutritionGoal.LOSE_WEIGHT:
            fat_percent = 0.25  # 25% от калорий
        elif goal == NutritionGoal.GAIN_MASS:
            fat_percent = 0.20  # 20% от калорий
        else:
            fat_percent = 0.30  # 30% от калорий
        
        fat_calories = calories * fat_percent
        fat_g = fat_calories / 9
        
        # Расчет углеводов (остаток калорий)
        protein_calories = protein_g * 4
        fat_calories = fat_g * 9
        remaining_calories = calories - protein_calories - fat_calories
        carbs_g = remaining_calories / 4
        
        return {
            'calories': round(calories),
            'protein_g': round(protein_g, 1),
            'fat_g': round(fat_g, 1),
            'carbs_g': round(carbs_g, 1),
            'protein_percent': round((protein_calories / calories) * 100, 1),
            'fat_percent': round((fat_calories / calories) * 100, 1),
            'carbs_percent': round((remaining_calories / calories) * 100, 1)
        }

    @staticmethod
    def calculate_water_intake(weight_kg: float, activity_level: str) -> float:
        """Рассчитать потребление воды"""
        base_water = weight_kg * 30  # мл в день
        
        activity_multipliers = {
            'sedentary': 1.0,
            'light': 1.1,
            'moderate': 1.2,
            'active': 1.3,
            'very_active': 1.4
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.0)
        return round(base_water * multiplier)

# База блюд с видео и изображениями
MEALS_DATABASE = {
    MealType.BREAKFAST: [
        Meal(
            name="Овсянка с ягодами и орехами",
            meal_type=MealType.BREAKFAST,
            calories=320,
            protein=12,
            fat=8,
            carbs=52,
            recipe="1. Сварите овсянку на воде или молоке\n2. Добавьте свежие ягоды\n3. Посыпьте измельченными орехами\n4. Добавьте мед по вкусу",
            image_url="assets/images/meals/breakfast/oatmeal_berries.jpg",
            video_url="https://youtu.be/breakfast_oatmeal_berries",
            ingredients=["овсянка", "ягоды", "орехи", "мед", "молоко"],
            cooking_time=10,
            difficulty=1,
            tags=["веган", "быстро", "здорово"],
            nutrition_notes="Богата клетчаткой и антиоксидантами"
        ),
        Meal(
            name="Творожная запеканка с фруктами",
            meal_type=MealType.BREAKFAST,
            calories=280,
            protein=18,
            fat=12,
            carbs=25,
            recipe="1. Смешайте творог с яйцами и медом\n2. Добавьте нарезанные фрукты\n3. Запекайте в духовке 20 минут при 180°C",
            image_url="assets/images/meals/breakfast/cottage_cheese_casserole.jpg",
            video_url="https://youtu.be/breakfast_cottage_cheese",
            ingredients=["творог", "яйца", "фрукты", "мед", "мука"],
            cooking_time=25,
            difficulty=2,
            tags=["белок", "сладкое", "запеченное"],
            nutrition_notes="Отличный источник белка и кальция"
        ),
        Meal(
            name="Протеиновый смузи с бананом",
            meal_type=MealType.BREAKFAST,
            calories=250,
            protein=25,
            fat=5,
            carbs=30,
            recipe="1. Смешайте протеин с молоком\n2. Добавьте банан и ягоды\n3. Взбейте в блендере до однородности",
            image_url="assets/images/meals/breakfast/protein_smoothie.jpg",
            video_url="https://youtu.be/breakfast_protein_smoothie",
            ingredients=["протеин", "банан", "ягоды", "молоко"],
            cooking_time=5,
            difficulty=1,
            tags=["протеин", "быстро", "смузи"],
            nutrition_notes="Идеально для набора мышечной массы"
        )
    ],
    MealType.LUNCH: [
        Meal(
            name="Куриная грудка с овощами и рисом",
            meal_type=MealType.LUNCH,
            calories=350,
            protein=35,
            fat=8,
            carbs=25,
            recipe="1. Запеките куриную грудку с специями\n2. Приготовьте овощи на пару\n3. Сварите бурый рис\n4. Подавайте вместе",
            image_url="assets/images/meals/lunch/chicken_vegetables.jpg",
            video_url="https://youtu.be/lunch_chicken_vegetables",
            ingredients=["куриная грудка", "овощи", "бурый рис", "специи"],
            cooking_time=30,
            difficulty=2,
            tags=["белок", "овощи", "сбалансированно"],
            nutrition_notes="Сбалансированное питание для любой цели"
        ),
        Meal(
            name="Лосось с киноа и овощами",
            meal_type=MealType.LUNCH,
            calories=420,
            protein=28,
            fat=22,
            carbs=35,
            recipe="1. Запеките лосось с лимоном и травами\n2. Сварите киноа\n3. Приготовьте овощи на гриле",
            image_url="assets/images/meals/lunch/salmon_quinoa.jpg",
            video_url="https://youtu.be/lunch_salmon_quinoa",
            ingredients=["лосось", "киноа", "овощи", "лимон", "травы"],
            cooking_time=25,
            difficulty=3,
            tags=["омега-3", "белок", "здоровые жиры"],
            nutrition_notes="Богат омега-3 жирными кислотами"
        ),
        Meal(
            name="Салат с тунцом и авокадо",
            meal_type=MealType.LUNCH,
            calories=280,
            protein=25,
            fat=12,
            carbs=15,
            recipe="1. Смешайте листья салата\n2. Добавьте тунец и авокадо\n3. Заправьте оливковым маслом и лимоном",
            image_url="assets/images/meals/lunch/tuna_avocado_salad.jpg",
            video_url="https://youtu.be/lunch_tuna_salad",
            ingredients=["тунец", "авокадо", "салат", "оливковое масло", "лимон"],
            cooking_time=10,
            difficulty=1,
            tags=["белок", "легкий", "салат"],
            nutrition_notes="Отлично подходит для похудения"
        )
    ],
    MealType.DINNER: [
        Meal(
            name="Индейка с гречкой и овощами",
            meal_type=MealType.DINNER,
            calories=380,
            protein=32,
            fat=10,
            carbs=40,
            recipe="1. Запеките индейку с специями\n2. Сварите гречку\n3. Приготовьте овощи на пару",
            image_url="assets/images/meals/dinner/turkey_buckwheat.jpg",
            video_url="https://youtu.be/dinner_turkey_buckwheat",
            ingredients=["индейка", "гречка", "овощи", "специи"],
            cooking_time=35,
            difficulty=2,
            tags=["белок", "медленные углеводы", "здорово"],
            nutrition_notes="Гречка - отличный источник медленных углеводов"
        ),
        Meal(
            name="Творог с фруктами и орехами",
            meal_type=MealType.DINNER,
            calories=220,
            protein=20,
            fat=8,
            carbs=18,
            recipe="1. Смешайте творог с фруктами\n2. Добавьте мед и орехи\n3. Посыпьте корицей",
            image_url="assets/images/meals/dinner/cottage_fruits.jpg",
            video_url="https://youtu.be/dinner_cottage_fruits",
            ingredients=["творог", "фрукты", "орехи", "мед", "корица"],
            cooking_time=5,
            difficulty=1,
            tags=["белок", "легкий", "сладкое"],
            nutrition_notes="Идеально для вечернего приема пищи"
        ),
        Meal(
            name="Омлет с овощами и сыром",
            meal_type=MealType.DINNER,
            calories=280,
            protein=18,
            fat=15,
            carbs=12,
            recipe="1. Взбейте яйца с молоком\n2. Добавьте нарезанные овощи\n3. Запекайте на сковороде с сыром",
            image_url="assets/images/meals/dinner/omelette_vegetables.jpg",
            video_url="https://youtu.be/dinner_omelette",
            ingredients=["яйца", "овощи", "сыр", "молоко"],
            cooking_time=15,
            difficulty=2,
            tags=["белок", "быстро", "запеченное"],
            nutrition_notes="Быстрый и питательный ужин"
        )
    ],
    MealType.SNACK: [
        Meal(
            name="Протеиновый коктейль с бананом",
            meal_type=MealType.SNACK,
            calories=180,
            protein=25,
            fat=3,
            carbs=15,
            recipe="1. Смешайте протеин с водой или молоком\n2. Добавьте банан\n3. Взбейте в блендере",
            image_url="assets/images/meals/snack/protein_shake.jpg",
            video_url="https://youtu.be/snack_protein_shake",
            ingredients=["протеин", "банан", "молоко"],
            cooking_time=3,
            difficulty=1,
            tags=["протеин", "быстро", "коктейль"],
            nutrition_notes="Отличный перекус после тренировки"
        ),
        Meal(
            name="Орехи и сухофрукты",
            meal_type=MealType.SNACK,
            calories=200,
            protein=6,
            fat=12,
            carbs=20,
            recipe="1. Смешайте различные орехи\n2. Добавьте сухофрукты\n3. Разделите на порции",
            image_url="assets/images/meals/snack/nuts_dried_fruits.jpg",
            video_url="https://youtu.be/snack_nuts_fruits",
            ingredients=["орехи", "сухофрукты"],
            cooking_time=2,
            difficulty=1,
            tags=["здоровые жиры", "энергия", "быстро"],
            nutrition_notes="Богаты полезными жирами и минералами"
        ),
        Meal(
            name="Йогурт с ягодами и медом",
            meal_type=MealType.SNACK,
            calories=150,
            protein=12,
            fat=5,
            carbs=18,
            recipe="1. Смешайте греческий йогурт с ягодами\n2. Добавьте мед\n3. Посыпьте орехами",
            image_url="assets/images/meals/snack/yogurt_berries.jpg",
            video_url="https://youtu.be/snack_yogurt_berries",
            ingredients=["греческий йогурт", "ягоды", "мед", "орехи"],
            cooking_time=3,
            difficulty=1,
            tags=["белок", "кальций", "быстро"],
            nutrition_notes="Отличный источник белка и кальция"
        )
    ]
}

class MealPlanner:
    """Планировщик питания"""

    def __init__(self):
        self.meals_database = MEALS_DATABASE
        self.calculator = NutritionCalculator()

    def generate_weekly_meal_plan(
        self,
        target_calories: int,
        target_protein: float,
        target_fat: float,
        target_carbs: float,
        goal: NutritionGoal,
        preferences: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """Генерировать план питания на неделю"""
        
        if preferences is None:
            preferences = []
        
        plan = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            plan[day] = {
                'breakfast': self._select_meal_for_goal(MealType.BREAKFAST, target_calories * 0.25, goal, preferences),
                'lunch': self._select_meal_for_goal(MealType.LUNCH, target_calories * 0.35, goal, preferences),
                'dinner': self._select_meal_for_goal(MealType.DINNER, target_calories * 0.30, goal, preferences),
                'snack': self._select_meal_for_goal(MealType.SNACK, target_calories * 0.10, goal, preferences)
            }
        
        return plan

    def _select_meal_for_goal(
        self,
        meal_type: MealType,
        target_calories: float,
        goal: NutritionGoal,
        preferences: List[str]
    ) -> Optional[Dict]:
        """Выбрать блюдо под цель"""
        
        available_meals = self.meals_database.get(meal_type, [])
        
        # Фильтруем по предпочтениям
        if preferences:
            filtered_meals = []
            for meal in available_meals:
                if any(pref.lower() in tag.lower() for tag in meal.tags for pref in preferences):
                    filtered_meals.append(meal)
            if filtered_meals:
                available_meals = filtered_meals
        
        # Выбираем блюдо в зависимости от цели
        if goal == NutritionGoal.LOSE_WEIGHT:
            # Предпочитаем низкокалорийные блюда с высоким белком
            suitable_meals = [m for m in available_meals if m.calories <= target_calories * 1.2 and m.protein >= 15]
        elif goal == NutritionGoal.GAIN_MASS:
            # Предпочитаем высококалорийные блюда с высоким белком
            suitable_meals = [m for m in available_meals if m.calories >= target_calories * 0.8 and m.protein >= 20]
        elif goal == NutritionGoal.CUT:
            # Предпочитаем низкокалорийные блюда
            suitable_meals = [m for m in available_meals if m.calories <= target_calories * 1.1]
        else:  # TONE
            # Сбалансированные блюда
            suitable_meals = [m for m in available_meals if abs(m.calories - target_calories) <= target_calories * 0.3]
        
        if not suitable_meals:
            suitable_meals = available_meals
        
        if not suitable_meals:
            return None
        
        # Выбираем случайное блюдо
        selected_meal = random.choice(suitable_meals)
        
        return {
            'name': selected_meal.name,
            'calories': selected_meal.calories,
            'protein': selected_meal.protein,
            'fat': selected_meal.fat,
            'carbs': selected_meal.carbs,
            'recipe': selected_meal.recipe,
            'image_url': selected_meal.image_url,
            'video_url': selected_meal.video_url,
            'ingredients': selected_meal.ingredients,
            'cooking_time': selected_meal.cooking_time,
            'difficulty': selected_meal.difficulty,
            'tags': selected_meal.tags,
            'nutrition_notes': selected_meal.nutrition_notes
        }

    def search_meals(
        self,
        query: str = "",
        meal_type: Optional[MealType] = None,
        max_calories: Optional[int] = None,
        min_protein: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """Поиск блюд по критериям"""
        
        results = []
        
        for meal_type_key, meals in self.meals_database.items():
            if meal_type and meal_type_key != meal_type:
                continue
                
            for meal in meals:
                # Фильтр по названию
                if query and query.lower() not in meal.name.lower():
                    continue
                
                # Фильтр по калориям
                if max_calories and meal.calories > max_calories:
                    continue
                
                # Фильтр по белку
                if min_protein and meal.protein < min_protein:
                    continue
                
                # Фильтр по тегам
                if tags and not any(tag.lower() in meal_tag.lower() for meal_tag in meal.tags for tag in tags):
                    continue
                
                results.append({
                    'name': meal.name,
                    'meal_type': meal.meal_type.value,
                    'calories': meal.calories,
                    'protein': meal.protein,
                    'fat': meal.fat,
                    'carbs': meal.carbs,
                    'recipe': meal.recipe,
                    'image_url': meal.image_url,
                    'video_url': meal.video_url,
                    'ingredients': meal.ingredients,
                    'cooking_time': meal.cooking_time,
                    'difficulty': meal.difficulty,
                    'tags': meal.tags,
                    'nutrition_notes': meal.nutrition_notes
                })
        
        return results

# Добавляю недостающие блюда для полноты базы
MEALS_DATABASE[MealType.BREAKFAST].extend([
    Meal(
        name="Яичница с овощами",
        meal_type=MealType.BREAKFAST,
        calories=220,
        protein=15,
        fat=12,
        carbs=8,
        recipe="1. Взбейте яйца\n2. Нарежьте овощи\n3. Обжарьте на сковороде",
        image_url="assets/images/meals/breakfast/scrambled_eggs.jpg",
        video_url="https://youtu.be/breakfast_scrambled_eggs",
        ingredients=["яйца", "овощи", "масло"],
        cooking_time=8,
        difficulty=1,
        tags=["белок", "быстро", "завтрак"],
        nutrition_notes="Отличный источник белка"
    )
])

MEALS_DATABASE[MealType.LUNCH].extend([
    Meal(
        name="Суп с курицей и овощами",
        meal_type=MealType.LUNCH,
        calories=180,
        protein=20,
        fat=6,
        carbs=15,
        recipe="1. Сварите куриный бульон\n2. Добавьте овощи\n3. Варите до готовности",
        image_url="assets/images/meals/lunch/chicken_soup.jpg",
        video_url="https://youtu.be/lunch_chicken_soup",
        ingredients=["курица", "овощи", "бульон"],
        cooking_time=40,
        difficulty=2,
        tags=["суп", "белок", "овощи"],
        nutrition_notes="Легкий и питательный обед"
    )
])

MEALS_DATABASE[MealType.DINNER].extend([
    Meal(
        name="Запеченная рыба с овощами",
        meal_type=MealType.DINNER,
        calories=250,
        protein=25,
        fat=8,
        carbs=12,
        recipe="1. Запеките рыбу в духовке\n2. Приготовьте овощи на пару\n3. Подавайте вместе",
        image_url="assets/images/meals/dinner/baked_fish.jpg",
        video_url="https://youtu.be/dinner_baked_fish",
        ingredients=["рыба", "овощи", "специи"],
        cooking_time=25,
        difficulty=2,
        tags=["рыба", "белок", "овощи"],
        nutrition_notes="Богата омега-3 жирными кислотами"
    )
])

MEALS_DATABASE[MealType.SNACK].extend([
    Meal(
        name="Творожная масса с фруктами",
        meal_type=MealType.SNACK,
        calories=120,
        protein=12,
        fat=4,
        carbs=12,
        recipe="1. Смешайте творог с фруктами\n2. Добавьте мед по вкусу",
        image_url="assets/images/meals/snack/cottage_fruit_mix.jpg",
        video_url="https://youtu.be/snack_cottage_fruit",
        ingredients=["творог", "фрукты", "мед"],
        cooking_time=3,
        difficulty=1,
        tags=["белок", "фрукты", "быстро"],
        nutrition_notes="Легкий и полезный перекус"
    )
])

# Глобальные экземпляры
nutrition_calculator = NutritionCalculator()
meal_planner = MealPlanner()

def get_meals_by_type(meal_type: MealType) -> List[Meal]:
    """Получить блюда по типу"""
    return MEALS_DATABASE.get(meal_type, [])

def get_meal_by_name(name: str) -> Optional[Meal]:
    """Получить блюдо по названию"""
    for meals in MEALS_DATABASE.values():
        for meal in meals:
            if meal.name.lower() == name.lower():
                return meal
    return None