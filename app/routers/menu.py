from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.nutrition import (
    nutrition_calculator, meal_planner, NutritionGoal, MealType,
    get_meals_by_type, get_meal_by_name
)
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_menu_messages
from app.utils.video_utils import send_exercise_demo
from app.db.models import ProgramLevel
import json

router = Router()


class MenuStates(StatesGroup):
    choosing_action = State()
    viewing_weekly_menu = State()
    searching_meals = State()
    personal_nutrition = State()
    choosing_nutrition_goal = State()


@router.message(Command("menu"))
async def menu_command(message: types.Message):
    """Команда меню"""
    await cleanup_menu_messages(message)
    await show_menu_menu(message)


async def show_menu_menu(message: types.Message):
    """Показать главное меню питания"""
    # Проверяем доступ пользователя
    if not await user_has_paid_access(message.from_user.id):
        await message.answer("❌ Для доступа к меню необходимо приобрести программу.")
        return
    
    text = (
        "🍲 <b>Меню на неделю</b>\n\n"
        "Выберите действие:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Персональное питание", callback_data="personal_nutrition")],
        [InlineKeyboardButton(text="📋 Посмотреть меню", callback_data="view_weekly_menu")],
        [InlineKeyboardButton(text="🔍 Поиск блюд", callback_data="search_meals")],
        [InlineKeyboardButton(text="🧠 AI анализ фото", callback_data="ai_photo_analysis")],
        [InlineKeyboardButton(text="💧 Калькулятор воды", callback_data="water_calculator")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_menu")
async def cabinet_menu_callback(callback: types.CallbackQuery):
    """Обработка кнопки меню из личного кабинета"""
    await cleanup_menu_messages(callback.message)
    await show_menu_menu(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "personal_nutrition")
async def personal_nutrition(callback: types.CallbackQuery, state: FSMContext):
    """Персональное питание"""
    await state.set_state(MenuStates.choosing_nutrition_goal)
    
    text = (
        "🎯 <b>Персональное питание</b>\n\n"
        "Выберите вашу цель:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Похудеть", callback_data="nutrition_goal:lose_weight")],
        [InlineKeyboardButton(text="💪 Набрать массу", callback_data="nutrition_goal:gain_mass")],
        [InlineKeyboardButton(text="✂️ Подсушиться", callback_data="nutrition_goal:cut")],
        [InlineKeyboardButton(text="🏃 Держать тонус", callback_data="nutrition_goal:tone")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("nutrition_goal:"))
async def nutrition_goal_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор цели питания"""
    goal = callback.data.split(":")[1]
    await state.update_data(nutrition_goal=goal)
    
    # Получаем данные пользователя
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return
    
    # Рассчитываем параметры питания
    bmr = nutrition_calculator.calculate_bmr(
        user.weight_kg or 70,
        user.height_cm or 170,
        user.age or 25,
        user.gender or 'male'
    )
    
    tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
    macros = nutrition_calculator.calculate_macros_for_goal(
        tdee,
        NutritionGoal(goal),
        user.weight_kg or 70
    )
    
    # Генерируем план питания
    meal_plan = meal_planner.generate_weekly_meal_plan(
        macros['calories'],
        macros['protein_g'],
        macros['fat_g'],
        macros['carbs_g'],
        NutritionGoal(goal)
    )
    
    # Сохраняем план в состоянии
    await state.update_data(meal_plan=meal_plan, macros=macros)
    await state.set_state(MenuStates.personal_nutrition)
    
    # Показываем план
    await show_nutrition_plan(callback.message, meal_plan, macros, NutritionGoal(goal))
    await callback.answer()


async def show_nutrition_plan(message: types.Message, meal_plan: dict, macros: dict, goal: NutritionGoal):
    """Показать план питания"""
    goal_names = {
        NutritionGoal.LOSE_WEIGHT: "Похудение",
        NutritionGoal.GAIN_MASS: "Набор массы",
        NutritionGoal.CUT: "Подсушивание",
        NutritionGoal.TONE: "Тонус"
    }
    
    text = (
        f"🍲 <b>Персональный план питания</b>\n\n"
        f"🎯 Цель: <b>{goal_names[goal]}</b>\n"
        f"📊 Калории: <b>{macros['calories']} ккал</b>\n"
        f"🥩 Белки: <b>{macros['protein_g']}г ({macros['protein_percent']}%)</b>\n"
        f"🥑 Жиры: <b>{macros['fat_g']}г ({macros['fat_percent']}%)</b>\n"
        f"🍞 Углеводы: <b>{macros['carbs_g']}г ({macros['carbs_percent']}%)</b>\n\n"
        f"Выберите день для просмотра меню:"
    )
    
    kb_buttons = []
    for day, day_meals in meal_plan.items():
        total_calories = sum(meal['calories'] for meal in day_meals.values() if meal)
        total_protein = sum(meal['protein'] for meal in day_meals.values() if meal)
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"📅 {day.title()}: {total_calories} ккал, {total_protein}г белка", 
                callback_data=f"show_nutrition_day:{day}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="personal_nutrition")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("show_nutrition_day:"))
async def show_nutrition_day(callback: types.CallbackQuery, state: FSMContext):
    """Показать питание на конкретный день"""
    day = callback.data.split(":")[1]
    
    # Получаем план из состояния
    data = await state.get_data()
    meal_plan = data.get("meal_plan", {})
    
    if day not in meal_plan:
        await callback.answer("День не найден")
        return
    
    day_meals = meal_plan[day]
    
    text = f"🍽️ <b>Меню на {day.title()}</b>\n\n"
    
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    
    meal_names = {
        'breakfast': '🌅 Завтрак',
        'lunch': '🌞 Обед',
        'dinner': '🌙 Ужин',
        'snack': '🍎 Перекус'
    }
    
    for meal_type, meal in day_meals.items():
        if meal:
            text += f"{meal_names[meal_type]}: <b>{meal['name']}</b>\n"
            text += f"📊 {meal['calories']} ккал | 🥩 {meal['protein']}г | 🥑 {meal['fat']}г | 🍞 {meal['carbs']}г\n\n"
            
            total_calories += meal['calories']
            total_protein += meal['protein']
            total_fat += meal['fat']
            total_carbs += meal['carbs']
    
    text += f"📈 <b>Итого за день:</b>\n"
    text += f"📊 {total_calories} ккал | 🥩 {total_protein}г | 🥑 {total_fat}г | 🍞 {total_carbs}г"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Рецепты", callback_data=f"show_recipes:{day}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="nutrition_goal_selected")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_recipes:"))
async def show_recipes(callback: types.CallbackQuery, state: FSMContext):
    """Показать рецепты на день"""
    day = callback.data.split(":")[1]
    
    # Получаем план из состояния
    data = await state.get_data()
    meal_plan = data.get("meal_plan", {})
    
    if day not in meal_plan:
        await callback.answer("День не найден")
        return
    
    day_meals = meal_plan[day]
    
    text = f"📋 <b>Рецепты на {day.title()}</b>\n\n"
    
    meal_names = {
        'breakfast': '🌅 Завтрак',
        'lunch': '🌞 Обед',
        'dinner': '🌙 Ужин',
        'snack': '🍎 Перекус'
    }
    
    kb_buttons = []
    
    for meal_type, meal in day_meals.items():
        if meal:
            text += f"{meal_names[meal_type]}: <b>{meal['name']}</b>\n"
            text += f"⏱️ Время приготовления: {meal['cooking_time']} мин\n"
            text += f"📝 Сложность: {'⭐' * meal['difficulty']}\n\n"
            
            kb_buttons.append([
                InlineKeyboardButton(
                    text=f"📖 {meal['name']}", 
                    callback_data=f"show_recipe:{day}:{meal_type}"
                )
            ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"show_nutrition_day:{day}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_recipe:"))
async def show_recipe(callback: types.CallbackQuery, state: FSMContext):
    """Показать рецепт блюда"""
    parts = callback.data.split(":")
    day = parts[1]
    meal_type = parts[2]
    
    # Получаем план из состояния
    data = await state.get_data()
    meal_plan = data.get("meal_plan", {})
    
    if day not in meal_plan or meal_type not in meal_plan[day]:
        await callback.answer("Блюдо не найдено")
        return
    
    meal = meal_plan[day][meal_type]
    
    text = f"📖 <b>{meal['name']}</b>\n\n"
    text += f"📊 <b>Пищевая ценность:</b>\n"
    text += f"• Калории: {meal['calories']} ккал\n"
    text += f"• Белки: {meal['protein']}г\n"
    text += f"• Жиры: {meal['fat']}г\n"
    text += f"• Углеводы: {meal['carbs']}г\n\n"
    
    text += f"🛒 <b>Ингредиенты:</b>\n"
    for ingredient in meal['ingredients']:
        text += f"• {ingredient}\n"
    
    text += f"\n👨‍🍳 <b>Рецепт:</b>\n{meal['recipe']}\n\n"
    
    if meal['nutrition_notes']:
        text += f"💡 <b>Примечание:</b> {meal['nutrition_notes']}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Видео рецепт", callback_data=f"show_recipe_video:{day}:{meal_type}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"show_recipes:{day}")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_recipe_video:"))
async def show_recipe_video(callback: types.CallbackQuery, state: FSMContext):
    """Показать видео рецепта"""
    parts = callback.data.split(":")
    day = parts[1]
    meal_type = parts[2]
    
    # Получаем план из состояния
    data = await state.get_data()
    meal_plan = data.get("meal_plan", {})
    
    if day not in meal_plan or meal_type not in meal_plan[day]:
        await callback.answer("Блюдо не найдено")
        return
    
    meal = meal_plan[day][meal_type]
    
    # Отправляем видео или ссылку
    video_url = meal['video_url']
    text = f"🎥 <b>Видео рецепт: {meal['name']}</b>\n\n"
    text += f"<a href='{video_url}'>Смотреть видео на YouTube</a>"
    
    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(lambda c: c.data == "view_weekly_menu")
async def view_weekly_menu(callback: types.CallbackQuery, state: FSMContext):
    """Показать меню на неделю"""
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return
    
    # Получаем персональные параметры питания
    bmr = nutrition_calculator.calculate_bmr(
        user.weight_kg or 70,
        user.height_cm or 170,
        user.age or 25,
        user.gender or 'male'
    )
    
    tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
    macros = nutrition_calculator.calculate_macros_for_goal(tdee, NutritionGoal.TONE, user.weight_kg or 70)
    
    # Генерируем план питания
    meal_plan = meal_planner.generate_weekly_meal_plan(
        macros['calories'],
        macros['protein_g'],
        macros['fat_g'],
        macros['carbs_g'],
        NutritionGoal.TONE
    )
    
    text = (
        f"🍲 <b>Меню на неделю</b>\n\n"
        f"Ваши параметры:\n"
        f"• Калории: {macros['calories']} ккал\n"
        f"• Белки: {macros['protein_g']}г\n"
        f"• Жиры: {macros['fat_g']}г\n"
        f"• Углеводы: {macros['carbs_g']}г\n\n"
        "Выберите день:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Понедельник", callback_data="menu_day:monday")],
        [InlineKeyboardButton(text="Вторник", callback_data="menu_day:tuesday")],
        [InlineKeyboardButton(text="Среда", callback_data="menu_day:wednesday")],
        [InlineKeyboardButton(text="Четверг", callback_data="menu_day:thursday")],
        [InlineKeyboardButton(text="Пятница", callback_data="menu_day:friday")],
        [InlineKeyboardButton(text="Суббота", callback_data="menu_day:saturday")],
        [InlineKeyboardButton(text="Воскресенье", callback_data="menu_day:sunday")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("menu_day:"))
async def show_menu_day(callback: types.CallbackQuery):
    """Показать меню на конкретный день"""
    day = callback.data.split(":")[1]
    
    # Получаем данные пользователя
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return
    
    # Рассчитываем параметры питания
    bmr = nutrition_calculator.calculate_bmr(
        user.weight_kg or 70,
        user.height_cm or 170,
        user.age or 25,
        user.gender or 'male'
    )
    
    tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
    macros = nutrition_calculator.calculate_macros_for_goal(tdee, NutritionGoal.TONE, user.weight_kg or 70)
    
    # Генерируем план питания
    meal_plan = meal_planner.generate_weekly_meal_plan(
        macros['calories'],
        macros['protein_g'],
        macros['fat_g'],
        macros['carbs_g'],
        NutritionGoal.TONE
    )
    
    if day not in meal_plan:
        await callback.answer("День не найден")
        return
    
    day_meals = meal_plan[day]
    
    text = f"🍽️ <b>Меню на {day.title()}</b>\n\n"
    
    meal_names = {
        'breakfast': '🌅 Завтрак',
        'lunch': '🌞 Обед',
        'dinner': '🌙 Ужин',
        'snack': '🍎 Перекус'
    }
    
    for meal_type, meal in day_meals.items():
        if meal:
            text += f"{meal_names[meal_type]}: <b>{meal['name']}</b>\n"
            text += f"📊 {meal['calories']} ккал | 🥩 {meal['protein']}г | 🥑 {meal['fat']}г | 🍞 {meal['carbs']}г\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="view_weekly_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "search_meals")
async def search_meals(callback: types.CallbackQuery, state: FSMContext):
    """Поиск блюд"""
    await state.set_state(MenuStates.searching_meals)
    
    text = (
        "🔍 <b>Поиск блюд</b>\n\n"
        "Выберите критерии поиска:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🥩 Высокий белок", callback_data="search_by_tag:белок")],
        [InlineKeyboardButton(text="🔥 Низкокалорийные", callback_data="search_by_calories:300")],
        [InlineKeyboardButton(text="🌅 Завтраки", callback_data="search_by_type:breakfast")],
        [InlineKeyboardButton(text="🌞 Обеды", callback_data="search_by_type:lunch")],
        [InlineKeyboardButton(text="🌙 Ужины", callback_data="search_by_type:dinner")],
        [InlineKeyboardButton(text="🍎 Перекусы", callback_data="search_by_type:snack")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("search_by_"))
async def search_by_criteria(callback: types.CallbackQuery):
    """Поиск по критериям"""
    search_type = callback.data.split(":")[0].replace("search_by_", "")
    value = callback.data.split(":")[1]
    
    if search_type == "tag":
        results = meal_planner.search_meals(tags=[value])
    elif search_type == "calories":
        results = meal_planner.search_meals(max_calories=int(value))
    elif search_type == "type":
        results = meal_planner.search_meals(meal_type=MealType(value))
    else:
        results = []
    
    if not results:
        text = "🔍 <b>Поиск блюд</b>\n\nПо вашему запросу ничего не найдено."
    else:
        text = f"🔍 <b>Результаты поиска</b>\n\n"
        for i, meal in enumerate(results[:10], 1):  # Показываем первые 10
            text += f"{i}. <b>{meal['name']}</b>\n"
            text += f"   📊 {meal['calories']} ккал | 🥩 {meal['protein']}г\n\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="search_meals")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "water_calculator")
async def water_calculator(callback: types.CallbackQuery):
    """Калькулятор воды"""
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return
    
    water_intake = nutrition_calculator.calculate_water_intake(
        user.weight_kg or 70,
        'moderate'
    )
    
    text = (
        f"💧 <b>Калькулятор воды</b>\n\n"
        f"Ваш вес: <b>{user.weight_kg or 70} кг</b>\n"
        f"Уровень активности: <b>Умеренный</b>\n\n"
        f"💧 <b>Рекомендуемое потребление воды:</b>\n"
        f"• <b>{water_intake} мл в день</b>\n"
        f"• <b>{water_intake // 8} мл за один прием</b> (8 раз в день)\n\n"
        f"💡 <b>Советы:</b>\n"
        f"• Пейте воду за 30 минут до еды\n"
        f"• Не пейте во время еды\n"
        f"• Увеличьте потребление при тренировках\n"
        f"• Следите за цветом мочи (должна быть светлой)"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await show_menu_menu(callback.message)
    await callback.answer()