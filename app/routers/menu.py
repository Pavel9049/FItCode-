from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.nutrition_utils import nutrition_calculator, meal_planner, nutrition_analyzer
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_menu_messages
from app.db.models import ProgramLevel
import json

router = Router()


class MenuStates(StatesGroup):
	choosing_action = State()
	viewing_weekly_menu = State()
	searching_meals = State()
	personal_nutrition = State()


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
		[InlineKeyboardButton(text="📋 Посмотреть меню", callback_data="view_weekly_menu")],
		[InlineKeyboardButton(text="📄 Скачать PDF", callback_data="download_menu_pdf")],
		[InlineKeyboardButton(text="🍽️ Персональное питание", callback_data="personal_nutrition")],
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
	macros = nutrition_calculator.calculate_macros_for_goal(tdee, 'tone', user.weight_kg or 70)
	
	# Генерируем план питания
	meal_plan = meal_planner.generate_weekly_meal_plan(
		macros['calories'],
		macros['protein_g'],
		macros['fat_g'],
		macros['carbs_g']
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
async def show_day_menu(callback: types.CallbackQuery, state: FSMContext):
	"""Показать меню на конкретный день"""
	day = callback.data.split(":")[1]
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Получаем план питания
	bmr = nutrition_calculator.calculate_bmr(
		user.weight_kg or 70,
		user.height_cm or 170,
		user.age or 25,
		user.gender or 'male'
	)
	
	tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
	macros = nutrition_calculator.calculate_macros_for_goal(tdee, 'tone', user.weight_kg or 70)
	
	meal_plan = meal_planner.generate_weekly_meal_plan(
		macros['calories'],
		macros['protein_g'],
		macros['fat_g'],
		macros['carbs_g']
	)
	
	day_meals = meal_plan.get(day, {})
	
	day_names = {
		'monday': 'Понедельник',
		'tuesday': 'Вторник',
		'wednesday': 'Среда',
		'thursday': 'Четверг',
		'friday': 'Пятница',
		'saturday': 'Суббота',
		'sunday': 'Воскресенье'
	}
	
	text = f"🍲 <b>Меню на {day_names[day]}</b>\n\n"
	
	total_calories = 0
	total_protein = 0
	total_fat = 0
	total_carbs = 0
	
	for meal_type, meal in day_meals.items():
		meal_type_names = {
			'breakfast': '🌅 Завтрак',
			'lunch': '🌞 Обед',
			'dinner': '🌙 Ужин',
			'snack': '🍎 Перекус'
		}
		
		text += f"{meal_type_names[meal_type]}:\n"
		text += f"• {meal['name']}\n"
		text += f"• {meal['calories']} ккал | {meal['protein']}Б | {meal['fat']}Ж | {meal['carbs']}У\n\n"
		
		total_calories += meal['calories']
		total_protein += meal['protein']
		total_fat += meal['fat']
		total_carbs += meal['carbs']
	
	text += f"<b>Итого за день:</b>\n"
	text += f"• {total_calories} ккал\n"
	text += f"• {total_protein}г белка\n"
	text += f"• {total_fat}г жиров\n"
	text += f"• {total_carbs}г углеводов"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📝 Рецепты", callback_data=f"show_recipes:{day}")],
		[InlineKeyboardButton(text="🔄 Обновить меню", callback_data="view_weekly_menu")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="view_weekly_menu")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_recipes:"))
async def show_recipes(callback: types.CallbackQuery, state: FSMContext):
	"""Показать рецепты для дня"""
	day = callback.data.split(":")[1]
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Получаем план питания
	bmr = nutrition_calculator.calculate_bmr(
		user.weight_kg or 70,
		user.height_cm or 170,
		user.age or 25,
		user.gender or 'male'
	)
	
	tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
	macros = nutrition_calculator.calculate_macros_for_goal(tdee, 'tone', user.weight_kg or 70)
	
	meal_plan = meal_planner.generate_weekly_meal_plan(
		macros['calories'],
		macros['protein_g'],
		macros['fat_g'],
		macros['carbs_g']
	)
	
	day_meals = meal_plan.get(day, {})
	
	day_names = {
		'monday': 'Понедельник',
		'tuesday': 'Вторник',
		'wednesday': 'Среда',
		'thursday': 'Четверг',
		'friday': 'Пятница',
		'saturday': 'Суббота',
		'sunday': 'Воскресенье'
	}
	
	text = f"📝 <b>Рецепты на {day_names[day]}</b>\n\n"
	
	for meal_type, meal in day_meals.items():
		meal_type_names = {
			'breakfast': '🌅 Завтрак',
			'lunch': '🌞 Обед',
			'dinner': '🌙 Ужин',
			'snack': '🍎 Перекус'
		}
		
		text += f"{meal_type_names[meal_type]}: {meal['name']}\n"
		text += f"<b>Рецепт:</b>\n{meal['recipe']}\n\n"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад к меню", callback_data=f"menu_day:{day}")],
		[InlineKeyboardButton(text="📋 К списку дней", callback_data="view_weekly_menu")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "personal_nutrition")
async def personal_nutrition(callback: types.CallbackQuery, state: FSMContext):
	"""Персональное питание"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Проверяем уровень пользователя
	if not user.level or user.level.value in ['beginner', 'novice']:
		text = (
			"🍽️ <b>Персональное питание</b>\n\n"
			"❌ Персональное питание доступно только для уровней 'Продвинутый' и 'Профессионал'.\n\n"
			"Обновите программу для доступа к этой функции."
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="💎 Обновить программу", callback_data="upgrade_program")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
		])
	else:
		# Рассчитываем персональное питание
		bmr = nutrition_calculator.calculate_bmr(
			user.weight_kg or 70,
			user.height_cm or 170,
			user.age or 25,
			user.gender or 'male'
		)
		
		tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
		
		text = (
			f"🍽️ <b>Персональное питание</b>\n\n"
			f"Ваши параметры:\n"
			f"• Вес: {user.weight_kg or 'Не указан'} кг\n"
			f"• Рост: {user.height_cm or 'Не указан'} см\n"
			f"• Возраст: {user.age or 'Не указан'} лет\n"
			f"• Пол: {user.gender or 'Не указан'}\n\n"
			f"<b>Расчеты:</b>\n"
			f"• Базовый метаболизм: {int(bmr)} ккал\n"
			f"• Общий расход энергии: {int(tdee)} ккал\n\n"
			"Выберите цель для расчета питания:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="💪 Набрать массу", callback_data="nutrition_goal:gain_mass")],
			[InlineKeyboardButton(text="🔥 Похудеть", callback_data="nutrition_goal:lose_weight")],
			[InlineKeyboardButton(text="✂️ Подсушиться", callback_data="nutrition_goal:cut")],
			[InlineKeyboardButton(text="🏃 Держать тонус", callback_data="nutrition_goal:tone")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
		])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("nutrition_goal:"))
async def show_nutrition_for_goal(callback: types.CallbackQuery, state: FSMContext):
	"""Показать питание для конкретной цели"""
	goal = callback.data.split(":")[1]
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Рассчитываем питание для цели
	bmr = nutrition_calculator.calculate_bmr(
		user.weight_kg or 70,
		user.height_cm or 170,
		user.age or 25,
		user.gender or 'male'
	)
	
	tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
	macros = nutrition_calculator.calculate_macros_for_goal(tdee, goal, user.weight_kg or 70)
	
	goal_names = {
		'gain_mass': 'Набор массы',
		'lose_weight': 'Похудение',
		'cut': 'Подсушивание',
		'tone': 'Поддержание тонуса'
	}
	
	advice = nutrition_analyzer.get_nutrition_advice(goal, user.weight_kg or 70, user.weight_kg or 70)
	water_intake = nutrition_analyzer.calculate_water_intake(user.weight_kg or 70, 'moderate')
	
	text = (
		f"🍽️ <b>Питание для цели: {goal_names[goal]}</b>\n\n"
		f"<b>Рекомендуемые параметры:</b>\n"
		f"• Калории: {macros['calories']} ккал\n"
		f"• Белки: {macros['protein_g']}г\n"
		f"• Жиры: {macros['fat_g']}г\n"
		f"• Углеводы: {macros['carbs_g']}г\n"
		f"• Вода: {water_intake}л\n\n"
		f"<b>Совет:</b>\n{advice}\n\n"
		"Хотите получить план питания на неделю?"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📋 Получить план", callback_data=f"generate_plan:{goal}")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="personal_nutrition")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("generate_plan:"))
async def generate_nutrition_plan(callback: types.CallbackQuery, state: FSMContext):
	"""Сгенерировать план питания для цели"""
	goal = callback.data.split(":")[1]
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Рассчитываем питание для цели
	bmr = nutrition_calculator.calculate_bmr(
		user.weight_kg or 70,
		user.height_cm or 170,
		user.age or 25,
		user.gender or 'male'
	)
	
	tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
	macros = nutrition_calculator.calculate_macros_for_goal(tdee, goal, user.weight_kg or 70)
	
	# Генерируем план питания
	meal_plan = meal_planner.generate_weekly_meal_plan(
		macros['calories'],
		macros['protein_g'],
		macros['fat_g'],
		macros['carbs_g']
	)
	
	goal_names = {
		'gain_mass': 'Набор массы',
		'lose_weight': 'Похудение',
		'cut': 'Подсушивание',
		'tone': 'Поддержание тонуса'
	}
	
	text = (
		f"📋 <b>План питания для {goal_names[goal]}</b>\n\n"
		f"Параметры: {macros['calories']} ккал, {macros['protein_g']}Б, {macros['fat_g']}Ж, {macros['carbs_g']}У\n\n"
		"Выберите день для просмотра меню:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="Понедельник", callback_data=f"personal_menu_day:monday:{goal}")],
		[InlineKeyboardButton(text="Вторник", callback_data=f"personal_menu_day:tuesday:{goal}")],
		[InlineKeyboardButton(text="Среда", callback_data=f"personal_menu_day:wednesday:{goal}")],
		[InlineKeyboardButton(text="Четверг", callback_data=f"personal_menu_day:thursday:{goal}")],
		[InlineKeyboardButton(text="Пятница", callback_data=f"personal_menu_day:friday:{goal}")],
		[InlineKeyboardButton(text="Суббота", callback_data=f"personal_menu_day:saturday:{goal}")],
		[InlineKeyboardButton(text="Воскресенье", callback_data=f"personal_menu_day:sunday:{goal}")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data=f"nutrition_goal:{goal}")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("personal_menu_day:"))
async def show_personal_menu_day(callback: types.CallbackQuery, state: FSMContext):
	"""Показать персональное меню на день"""
	parts = callback.data.split(":")
	day = parts[1]
	goal = parts[2]
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Рассчитываем питание для цели
	bmr = nutrition_calculator.calculate_bmr(
		user.weight_kg or 70,
		user.height_cm or 170,
		user.age or 25,
		user.gender or 'male'
	)
	
	tdee = nutrition_calculator.calculate_tdee(bmr, 'moderate')
	macros = nutrition_calculator.calculate_macros_for_goal(tdee, goal, user.weight_kg or 70)
	
	# Генерируем план питания
	meal_plan = meal_planner.generate_weekly_meal_plan(
		macros['calories'],
		macros['protein_g'],
		macros['fat_g'],
		macros['carbs_g']
	)
	
	day_meals = meal_plan.get(day, {})
	
	day_names = {
		'monday': 'Понедельник',
		'tuesday': 'Вторник',
		'wednesday': 'Среда',
		'thursday': 'Четверг',
		'friday': 'Пятница',
		'saturday': 'Суббота',
		'sunday': 'Воскресенье'
	}
	
	goal_names = {
		'gain_mass': 'Набор массы',
		'lose_weight': 'Похудение',
		'cut': 'Подсушивание',
		'tone': 'Поддержание тонуса'
	}
	
	text = f"🍽️ <b>Персональное меню на {day_names[day]}</b>\n"
	text += f"Цель: {goal_names[goal]}\n\n"
	
	total_calories = 0
	total_protein = 0
	total_fat = 0
	total_carbs = 0
	
	for meal_type, meal in day_meals.items():
		meal_type_names = {
			'breakfast': '🌅 Завтрак',
			'lunch': '🌞 Обед',
			'dinner': '🌙 Ужин',
			'snack': '🍎 Перекус'
		}
		
		text += f"{meal_type_names[meal_type]}:\n"
		text += f"• {meal['name']}\n"
		text += f"• {meal['calories']} ккал | {meal['protein']}Б | {meal['fat']}Ж | {meal['carbs']}У\n\n"
		
		total_calories += meal['calories']
		total_protein += meal['protein']
		total_fat += meal['fat']
		total_carbs += meal['carbs']
	
	text += f"<b>Итого за день:</b>\n"
	text += f"• {total_calories} ккал\n"
	text += f"• {total_protein}г белка\n"
	text += f"• {total_fat}г жиров\n"
	text += f"• {total_carbs}г углеводов"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📝 Рецепты", callback_data=f"personal_recipes:{day}:{goal}")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data=f"generate_plan:{goal}")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "search_meals")
async def search_meals(callback: types.CallbackQuery, state: FSMContext):
	"""Поиск блюд"""
	text = (
		"🔍 <b>Поиск блюд</b>\n\n"
		"Введите название блюда или ингредиент для поиска.\n"
		"Например: 'курица', 'овощи', 'протеин'"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(MenuStates.searching_meals)
	await callback.answer()


@router.message(MenuStates.searching_meals)
async def process_meal_search(message: types.Message, state: FSMContext):
	"""Обработка поиска блюд"""
	query = message.text
	
	# Ищем блюда
	results = meal_planner.search_meals(query)
	
	if not results:
		text = f"🔍 <b>Поиск: '{query}'</b>\n\nНичего не найдено. Попробуйте другой запрос."
	else:
		text = f"🔍 <b>Поиск: '{query}'</b>\n\nНайдено {len(results)} блюд:\n\n"
		
		for i, meal in enumerate(results[:10], 1):  # Показываем первые 10
			meal_type_names = {
				'breakfast': '🌅 Завтрак',
				'lunch': '🌞 Обед',
				'dinner': '🌙 Ужин',
				'snack': '🍎 Перекус'
			}
			
			text += f"<b>{i}.</b> {meal['name']}\n"
			text += f"   {meal['calories']} ккал | {meal['protein']}Б | {meal['fat']}Ж | {meal['carbs']}У\n"
			text += f"   {meal_type_names.get(meal.get('meal_type', ''), '')}\n\n"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔍 Новый поиск", callback_data="search_meals")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")
	await state.clear()


@router.callback_query(lambda c: c.data == "ai_photo_analysis")
async def ai_photo_analysis(callback: types.CallbackQuery, state: FSMContext):
	"""AI анализ фото блюда"""
	text = (
		"🧠 <b>AI анализ фото блюда</b>\n\n"
		"Отправьте фото блюда, и я определю примерные КБЖУ.\n\n"
		"<i>Примечание: Это приблизительная оценка. Для точных данных используйте кухонные весы.</i>"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(MenuStates.searching_meals)  # Временно используем это состояние
	await callback.answer()


@router.callback_query(lambda c: c.data == "water_calculator")
async def water_calculator(callback: types.CallbackQuery, state: FSMContext):
	"""Калькулятор воды"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	water_intake = nutrition_analyzer.calculate_water_intake(user.weight_kg or 70, 'moderate')
	
	text = (
		f"💧 <b>Калькулятор воды</b>\n\n"
		f"Ваш вес: {user.weight_kg or 'Не указан'} кг\n"
		f"Уровень активности: Умеренный\n\n"
		f"<b>Рекомендуемое потребление воды:</b>\n"
		f"• {water_intake} литров в день\n\n"
		f"<b>Советы:</b>\n"
		f"• Пейте воду равномерно в течение дня\n"
		f"• Увеличьте потребление во время тренировок\n"
		f"• Следите за цветом мочи (должна быть светлой)"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "menu")
async def back_to_menu(callback: types.CallbackQuery):
	"""Возврат в главное меню питания"""
	await show_menu_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "download_menu_pdf")
async def download_menu_pdf(callback: types.CallbackQuery):
	"""Скачать меню в PDF"""
	text = (
		"📄 <b>Скачать меню в PDF</b>\n\n"
		"Функция находится в разработке.\n"
		"Скоро вы сможете скачать свое персональное меню в формате PDF."
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()