from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.workouts import (
    get_muscle_groups, get_split_info, get_exercises_for_muscle_group,
    generate_workout_plan, estimate_working_weight, WorkoutGoal, WorkoutLevel, EquipmentType
)
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_workout_messages
from app.utils.video_utils import send_exercise_demo, send_workout_plan_with_media
from app.db.models import ProgramLevel
import json

router = Router()


class WorkoutStates(StatesGroup):
    choosing_workout_type = State()
    choosing_muscle_group = State()
    choosing_goal = State()
    choosing_equipment = State()
    viewing_exercises = State()
    generating_plan = State()


@router.message(Command("workouts"))
async def workouts_command(message: types.Message):
    """Команда тренировок"""
    await cleanup_workout_messages(message)
    await show_workouts_menu(message)


async def show_workouts_menu(message: types.Message):
    """Показать главное меню тренировок"""
    # Проверяем доступ пользователя
    if not await user_has_paid_access(message.from_user.id):
        await message.answer("❌ Для доступа к тренировкам необходимо приобрести программу.")
        return
    
    text = (
        "🏋️‍♂️ <b>Тренировки</b>\n\n"
        "Выберите тип тренировки:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Персональный план", callback_data="workout_type:personal")],
        [InlineKeyboardButton(text="🏠 Домашние тренировки", callback_data="workout_type:bodyweight")],
        [InlineKeyboardButton(text="🏢 Сплит-тренировки", callback_data="workout_type:split")],
        [InlineKeyboardButton(text="💪 По группам мышц", callback_data="workout_type:muscle_groups")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "workouts")
async def workouts_callback(callback: types.CallbackQuery):
    """Обработка кнопки тренировок из личного кабинета"""
    print(f"🏋️‍♂️ Получен callback workouts от пользователя {callback.from_user.id}")
    await cleanup_workout_messages(callback.message)
    await show_workouts_menu(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "workout_type:personal")
async def personal_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Персональный план тренировок"""
    await state.set_state(WorkoutStates.choosing_goal)
    
    text = (
        "🎯 <b>Персональный план тренировок</b>\n\n"
        "Выберите вашу цель:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Похудеть", callback_data="goal:lose_weight")],
        [InlineKeyboardButton(text="💪 Набрать массу", callback_data="goal:gain_mass")],
        [InlineKeyboardButton(text="✂️ Подсушиться", callback_data="goal:cut")],
        [InlineKeyboardButton(text="🏃 Держать тонус", callback_data="goal:tone")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("goal:"))
async def goal_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор цели тренировок"""
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    await state.set_state(WorkoutStates.choosing_equipment)
    
    text = (
        "🏋️‍♂️ <b>Выберите доступное оборудование</b>\n\n"
        "Отметьте все, что у вас есть:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Только тело", callback_data="equipment:bodyweight")],
        [InlineKeyboardButton(text="🏋️‍♂️ Гантели", callback_data="equipment:dumbbells")],
        [InlineKeyboardButton(text="⚖️ Штанга", callback_data="equipment:barbell")],
        [InlineKeyboardButton(text="🏢 Тренажеры", callback_data="equipment:machines")],
        [InlineKeyboardButton(text="🎯 Резинки", callback_data="equipment:resistance_bands")],
        [InlineKeyboardButton(text="✅ Все оборудование", callback_data="equipment:all")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:personal")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("equipment:"))
async def equipment_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор оборудования"""
    equipment = callback.data.split(":")[1]
    
    # Получаем данные пользователя
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return
    
    # Определяем доступное оборудование
    if equipment == "all":
        available_equipment = [e for e in EquipmentType]
    else:
        available_equipment = [EquipmentType(equipment)]
    
    # Получаем цель из состояния
    data = await state.get_data()
    goal = WorkoutGoal(data.get("goal", "tone"))
    
    # Определяем уровень пользователя
    level = WorkoutLevel(user.level.value if user.level else "beginner")
    
    # Генерируем персональный план
    workout_plan = generate_workout_plan(
        user_weight=user.weight_kg or 70,
        user_height=user.height_cm or 170,
        user_gender=user.gender or "male",
        user_age=user.age or 25,
        goal=goal,
        level=level,
        available_equipment=available_equipment
    )
    
    # Сохраняем план в состоянии
    await state.update_data(workout_plan=workout_plan)
    await state.set_state(WorkoutStates.generating_plan)
    
    # Показываем план
    await show_workout_plan(callback.message, workout_plan, goal, level)
    await callback.answer()


async def show_workout_plan(message: types.Message, workout_plan: dict, goal: WorkoutGoal, level: WorkoutLevel):
    """Показать план тренировок"""
    goal_names = {
        WorkoutGoal.LOSE_WEIGHT: "Похудение",
        WorkoutGoal.GAIN_MASS: "Набор массы",
        WorkoutGoal.CUT: "Подсушивание",
        WorkoutGoal.TONE: "Тонус"
    }
    
    level_names = {
        WorkoutLevel.BEGINNER: "Начинающий",
        WorkoutLevel.NOVICE: "Новичок",
        WorkoutLevel.ADVANCED: "Продвинутый",
        WorkoutLevel.PRO: "Профессионал"
    }
    
    text = (
        f"📋 <b>Персональный план тренировок</b>\n\n"
        f"🎯 Цель: <b>{goal_names[goal]}</b>\n"
        f"📊 Уровень: <b>{level_names[level]}</b>\n\n"
        f"Выберите день для просмотра детального плана:"
    )
    
    kb_buttons = []
    for day, day_plan in workout_plan.items():
        if day_plan["muscle_groups"] == ["rest"]:
            continue
        
        muscle_groups = ", ".join([mg.title() for mg in day_plan["muscle_groups"]])
        exercise_count = len(day_plan["exercises"])
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"📅 {day.title()}: {muscle_groups} ({exercise_count} упр.)", 
                callback_data=f"show_day:{day}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:personal")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("show_day:"))
async def show_day_workout(callback: types.CallbackQuery, state: FSMContext):
    """Показать тренировку на конкретный день"""
    day = callback.data.split(":")[1]
    
    # Получаем план из состояния
    data = await state.get_data()
    workout_plan = data.get("workout_plan", {})
    
    if day not in workout_plan:
        await callback.answer("День не найден")
        return
    
    # Отправляем план с медиа
    await send_workout_plan_with_media(callback.message, workout_plan, day)
    await callback.answer()


@router.callback_query(lambda c: c.data == "workout_type:bodyweight")
async def bodyweight_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Домашние тренировки"""
    await state.set_state(WorkoutStates.choosing_workout_type)
    
    text = (
        "🏠 <b>Домашние тренировки</b>\n\n"
        "Выберите группу мышц:"
    )
    
    muscle_groups = get_muscle_groups()
    kb_buttons = []
    
    for muscle in muscle_groups:
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"💪 {muscle.title()}", 
                callback_data=f"bodyweight_muscle:{muscle}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "workout_type:split")
async def split_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Сплит-тренировки"""
    await state.set_state(WorkoutStates.choosing_workout_type)
    
    text = (
        "🏢 <b>Сплит-тренировки</b>\n\n"
        "Выберите тип сплита:"
    )
    
    splits = get_split_info()
    kb_buttons = []
    
    for split_name, split_info in splits.items():
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🏋️‍♂️ {split_info['title']}", 
                callback_data=f"split:{split_name}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "workout_type:muscle_groups")
async def muscle_groups_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Тренировки по группам мышц"""
    await state.set_state(WorkoutStates.choosing_muscle_group)
    
    text = (
        "💪 <b>Тренировки по группам мышц</b>\n\n"
        "Выберите группу мышц:"
    )
    
    muscle_groups = get_muscle_groups()
    kb_buttons = []
    
    for muscle in muscle_groups:
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"💪 {muscle.title()}", 
                callback_data=f"muscle_group:{muscle}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("bodyweight_muscle:"))
async def show_bodyweight_exercises(callback: types.CallbackQuery, state: FSMContext):
    """Показать домашние упражнения для группы мышц"""
    muscle_group = callback.data.split(":")[1]
    await state.set_state(WorkoutStates.viewing_exercises)
    
    # Получаем упражнения для начинающего уровня (домашние)
    exercises = get_exercises_for_muscle_group(muscle_group, WorkoutLevel.BEGINNER)
    
    text = f"🏠 <b>Домашние упражнения: {muscle_group.title()}</b>\n\n"
    
    kb_buttons = []
    for i, exercise in enumerate(exercises[:5]):  # Показываем первые 5 упражнений
        text += f"{i+1}. {exercise.name}\n"
        text += f"   {exercise.description}\n\n"
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🎥 {exercise.name}", 
                callback_data=f"show_exercise_video:{muscle_group}:beginner:{exercise.name}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:bodyweight")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("muscle_group:"))
async def show_muscle_exercises(callback: types.CallbackQuery, state: FSMContext):
    """Показать упражнения для группы мышц"""
    muscle_group = callback.data.split(":")[1]
    await state.set_state(WorkoutStates.viewing_exercises)
    
    user = await get_user_by_tg_id(callback.from_user.id)
    level = WorkoutLevel(user.level.value if user and user.level else "beginner")
    
    exercises = get_exercises_for_muscle_group(muscle_group, level)
    
    text = f"💪 <b>Упражнения: {muscle_group.title()}</b>\n\n"
    text += f"Уровень: <b>{level.value.title()}</b>\n\n"
    
    kb_buttons = []
    for i, exercise in enumerate(exercises[:5]):  # Показываем первые 5 упражнений
        text += f"{i+1}. {exercise.name}\n"
        text += f"   {exercise.description}\n\n"
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🎥 {exercise.name}", 
                callback_data=f"show_exercise_video:{muscle_group}:{level.value}:{exercise.name}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:muscle_groups")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_exercise_video:"))
async def show_exercise_video(callback: types.CallbackQuery):
    """Показать видео упражнения"""
    parts = callback.data.split(":")
    muscle_group = parts[1]
    level = parts[2]
    exercise_name = parts[3]
    
    # Находим упражнение в базе
    exercises = get_exercises_for_muscle_group(muscle_group, WorkoutLevel(level))
    exercise = next((ex for ex in exercises if ex.name == exercise_name), None)
    
    if exercise:
        # Отправляем демонстрацию упражнения
        await send_exercise_demo(
            callback.message,
            exercise.name,
            exercise.muscle_group,
            exercise.level.value,
            exercise.description,
            exercise.target_muscles,
            exercise.instructions
        )
    else:
        await callback.message.answer("Упражнение не найдено")
    
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("split:"))
async def show_split_workout(callback: types.CallbackQuery):
    """Показать сплит-тренировку"""
    split_name = callback.data.split(":")[1]
    splits = get_split_info()
    
    if split_name not in splits:
        await callback.answer("Сплит не найден")
        return
    
    split_info = splits[split_name]
    
    text = f"🏢 <b>{split_info['title']}</b>\n\n"
    text += f"{split_info['description']}\n\n"
    text += "Дни тренировок:\n"
    
    for day, muscles in split_info['days'].items():
        text += f"• <b>{day.title()}:</b> {', '.join(muscles)}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Смотреть упражнения", callback_data=f"show_split_exercises:{split_name}")],
        [InlineKeyboardButton(text="📋 Скачать план", callback_data=f"download_split:{split_name}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:split")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_workouts")
async def back_to_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в меню тренировок"""
    await state.clear()
    await show_workouts_menu(callback.message)
    await callback.answer()