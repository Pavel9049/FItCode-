from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.workouts import (
	get_muscle_groups, get_split_info, get_exercises_for_muscle_group,
	get_bodyweight_exercises, generate_week_plan, estimate_working_weight
)
from app.services.programs import get_paid_programs
from app.db.models import ProgramLevel, User
from app.db.session import get_session_maker
from sqlalchemy import select
from datetime import datetime
import json

router = Router()


class WorkoutStates(StatesGroup):
	choosing_type = State()
	choosing_split = State()
	choosing_muscle_group = State()
	viewing_exercises = State()
	generating_plan = State()


@router.message(Command("workouts"))
async def workouts_menu(message: types.Message):
	"""Главное меню тренировок"""
	# Проверяем доступ пользователя
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == message.from_user.id)
		)).scalar_one_or_none()
		
		if not user or not user.level:
			await message.answer("❌ Для доступа к тренировкам необходимо приобрести программу.")
			return

	text = (
		f"🏋️‍♂️ <b>Тренировки</b>\n\n"
		f"Ваш уровень: <b>{user.level.value.title()}</b>\n\n"
		"Выберите тип тренировки:"
	)

	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🏠 Домашние тренировки (без инвентаря)", callback_data="workout_type:bodyweight")],
		[InlineKeyboardButton(text="🏋️‍♂️ Сплит-тренировки (с инвентарем)", callback_data="workout_type:split")],
		[InlineKeyboardButton(text="🎯 Персональный план на неделю", callback_data="workout_type:personal")],
		[InlineKeyboardButton(text="📊 По группам мышц", callback_data="workout_type:muscle_groups")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_cabinet")]
	])

	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "workouts")
async def workouts_callback(callback: types.CallbackQuery):
	"""Обработка кнопки тренировок из личного кабинета"""
	await workouts_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("workout_type:"))
async def workout_type_selected(callback: types.CallbackQuery, state: FSMContext):
	"""Выбор типа тренировки"""
	workout_type = callback.data.split(":")[1]
	await state.update_data(workout_type=workout_type)
	
	if workout_type == "bodyweight":
		await show_bodyweight_menu(callback.message, state)
	elif workout_type == "split":
		await show_split_menu(callback.message, state)
	elif workout_type == "personal":
		await show_personal_plan_menu(callback.message, state)
	elif workout_type == "muscle_groups":
		await show_muscle_groups_menu(callback.message, state)
	
	await callback.answer()


async def show_bodyweight_menu(message: types.Message, state: FSMContext):
	"""Меню домашних тренировок"""
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == message.from_user.id)
		)).scalar_one_or_none()
		
		level = user.level if user else ProgramLevel.beginner
		exercises = get_bodyweight_exercises(level)
		
		text = (
			f"🏠 <b>Домашние тренировки</b>\n\n"
			f"Уровень: <b>{level.value.title()}</b>\n"
			f"Количество упражнений: <b>{len(exercises)}</b>\n\n"
			"Выберите действие:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🎯 Сгенерировать план на неделю", callback_data="generate_bodyweight_plan")],
			[InlineKeyboardButton(text="📋 Показать все упражнения", callback_data="show_bodyweight_exercises")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")]
		])
		
		await message.edit_text(text, reply_markup=kb, parse_mode="HTML")


async def show_split_menu(message: types.Message, state: FSMContext):
	"""Меню сплит-тренировок"""
	splits = get_split_info()
	
	text = "🏋️‍♂️ <b>Сплит-тренировки</b>\n\nВыберите сплит:"
	
	buttons = []
	for split in splits:
		groups_text = ", ".join(split["groups"])
		buttons.append([
			InlineKeyboardButton(
				text=f"{split['day']} ({groups_text})", 
				callback_data=f"split:{split['day']}"
			)
		])
	
	buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
	kb = InlineKeyboardMarkup(inline_keyboard=buttons)
	
	await message.edit_text(text, reply_markup=kb, parse_mode="HTML")


async def show_muscle_groups_menu(message: types.Message, state: FSMContext):
	"""Меню групп мышц"""
	muscle_groups = get_muscle_groups()
	
	text = "📊 <b>Упражнения по группам мышц</b>\n\nВыберите группу мышц:"
	
	buttons = []
	for group in muscle_groups:
		group_name = {
			"back": "Спина",
			"chest": "Грудь", 
			"biceps": "Бицепс",
			"triceps": "Трицепс",
			"shoulders": "Плечи",
			"legs": "Ноги",
			"abs": "Пресс",
			"forearms": "Предплечья"
		}.get(group, group.title())
		
		buttons.append([
			InlineKeyboardButton(text=group_name, callback_data=f"muscle_group:{group}")
		])
	
	buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
	kb = InlineKeyboardMarkup(inline_keyboard=buttons)
	
	await message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("split:"))
async def split_selected(callback: types.CallbackQuery, state: FSMContext):
	"""Выбор сплита"""
	split_name = callback.data.split(":")[1]
	splits = get_split_info()
	selected_split = next((s for s in splits if s["day"] == split_name), None)
	
	if not selected_split:
		await callback.answer("Сплит не найден")
		return
	
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		level = user.level if user else ProgramLevel.beginner
		
		text = f"🏋️‍♂️ <b>{split_name} Day</b>\n\n"
		text += f"Уровень: <b>{level.value.title()}</b>\n\n"
		
		exercises_text = ""
		for group in selected_split["groups"]:
			group_exercises = get_exercises_for_muscle_group(group, level)
			group_name = {
				"back": "Спина",
				"chest": "Грудь",
				"biceps": "Бицепс", 
				"triceps": "Трицепс",
				"shoulders": "Плечи",
				"legs": "Ноги",
				"abs": "Пресс",
				"forearms": "Предплечья"
			}.get(group, group.title())
			
			exercises_text += f"<b>{group_name}:</b>\n"
			for i, ex in enumerate(group_exercises[:3], 1):
				exercises_text += f"{i}. {ex['name']}\n"
			exercises_text += "\n"
		
		text += exercises_text
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🎯 Сгенерировать план", callback_data=f"generate_split_plan:{split_name}")],
			[InlineKeyboardButton(text="📋 Показать все упражнения", callback_data=f"show_split_exercises:{split_name}")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:split")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data.startswith("muscle_group:"))
async def muscle_group_selected(callback: types.CallbackQuery, state: FSMContext):
	"""Выбор группы мышц"""
	muscle_group = callback.data.split(":")[1]
	
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		level = user.level if user else ProgramLevel.beginner
		exercises = get_exercises_for_muscle_group(muscle_group, level)
		
		group_name = {
			"back": "Спина",
			"chest": "Грудь",
			"biceps": "Бицепс",
			"triceps": "Трицепс", 
			"shoulders": "Плечи",
			"legs": "Ноги",
			"abs": "Пресс",
			"forearms": "Предплечья"
		}.get(muscle_group, muscle_group.title())
		
		text = f"📊 <b>{group_name}</b>\n\n"
		text += f"Уровень: <b>{level.value.title()}</b>\n"
		text += f"Количество упражнений: <b>{len(exercises)}</b>\n\n"
		
		for i, ex in enumerate(exercises, 1):
			text += f"<b>{i}.</b> {ex['name']}\n"
			text += f"   {ex['description']}\n\n"
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🎥 Видео упражнений", callback_data=f"show_exercise_videos:{muscle_group}")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:muscle_groups")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_exercise_videos:"))
async def show_exercise_videos(callback: types.CallbackQuery, state: FSMContext):
	"""Показать видео упражнений"""
	muscle_group = callback.data.split(":")[1]
	
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		level = user.level if user else ProgramLevel.beginner
		exercises = get_exercises_for_muscle_group(muscle_group, level)
		
		group_name = {
			"back": "Спина",
			"chest": "Грудь",
			"biceps": "Бицепс",
			"triceps": "Трицепс",
			"shoulders": "Плечи", 
			"legs": "Ноги",
			"abs": "Пресс",
			"forearms": "Предплечья"
		}.get(muscle_group, muscle_group.title())
		
		text = f"🎥 <b>Видео упражнений: {group_name}</b>\n\n"
		
		buttons = []
		for i, ex in enumerate(exercises, 1):
			text += f"<b>{i}.</b> {ex['name']}\n"
			buttons.append([
				InlineKeyboardButton(
					text=f"🎥 {ex['name']}", 
					url=ex['video_url']
				)
			])
		
		buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"muscle_group:{muscle_group}")])
		kb = InlineKeyboardMarkup(inline_keyboard=buttons)
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "generate_bodyweight_plan")
async def generate_bodyweight_plan(callback: types.CallbackQuery, state: FSMContext):
	"""Генерация плана домашних тренировок"""
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		plan = generate_week_plan(user.level, "tone", user.weight_kg, False)
		
		text = "🏠 <b>План домашних тренировок на неделю</b>\n\n"
		
		for day, exercises in plan["days"].items():
			day_name = {
				0: "Понедельник",
				1: "Вторник", 
				2: "Среда",
				3: "Четверг",
				4: "Пятница",
				5: "Суббота",
				6: "Воскресенье"
			}.get(datetime.strptime(day, "%Y-%m-%d").weekday(), day)
			
			text += f"<b>{day_name}:</b>\n"
			for ex in exercises:
				text += f"• {ex['name']} - {ex['sets']}x{ex['reps']}\n"
			text += "\n"
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="💾 Сохранить план", callback_data="save_workout_plan")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:bodyweight")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data.startswith("generate_split_plan:"))
async def generate_split_plan(callback: types.CallbackQuery, state: FSMContext):
	"""Генерация плана сплит-тренировок"""
	split_name = callback.data.split(":")[1]
	
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		plan = generate_week_plan(user.level, "gain_mass", user.weight_kg, True)
		
		text = f"🏋️‍♂️ <b>План сплит-тренировок на неделю</b>\n\n"
		
		for day, split_data in plan["days"].items():
			day_name = {
				0: "Понедельник",
				1: "Вторник",
				2: "Среда", 
				3: "Четверг",
				4: "Пятница",
				5: "Суббота",
				6: "Воскресенье"
			}.get(datetime.strptime(day, "%Y-%m-%d").weekday(), day)
			
			text += f"<b>{day_name}:</b>\n"
			for group_data in split_data:
				group_name = {
					"back": "Спина",
					"chest": "Грудь",
					"biceps": "Бицепс",
					"triceps": "Трицепс",
					"shoulders": "Плечи",
					"legs": "Ноги", 
					"abs": "Пресс",
					"forearms": "Предплечья"
				}.get(group_data["group"], group_data["group"].title())
				
				text += f"  <b>{group_name}:</b>\n"
				for ex in group_data["exercises"]:
					text += f"  • {ex['name']} - {ex['sets']}x{ex['reps']} ({ex['weight']}кг)\n"
			text += "\n"
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="💾 Сохранить план", callback_data="save_workout_plan")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data=f"split:{split_name}")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_cabinet")
async def back_to_cabinet(callback: types.CallbackQuery):
	"""Возврат в личный кабинет"""
	from app.routers.cabinet import show_cabinet
	await show_cabinet(callback.message)
	await callback.answer()


async def show_personal_plan_menu(message: types.Message, state: FSMContext):
	"""Меню персонального плана"""
	text = "🎯 <b>Персональный план на неделю</b>\n\nВыберите цель:"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💪 Набрать массу", callback_data="goal:gain_mass")],
		[InlineKeyboardButton(text="🔥 Похудеть", callback_data="goal:lose_weight")],
		[InlineKeyboardButton(text="✂️ Подсушиться", callback_data="goal:cut")],
		[InlineKeyboardButton(text="🏃 Держать тонус", callback_data="goal:tone")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")]
	])
	
	await message.edit_text(text, reply_markup=kb, parse_mode="HTML")