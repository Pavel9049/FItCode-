from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.workouts import (
    get_muscle_groups, get_split_info, get_exercises_for_muscle_group,
    get_bodyweight_exercises, generate_week_plan, estimate_working_weight
)
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_workout_messages
from app.utils.video_utils import send_exercise_demo
from app.db.models import ProgramLevel
import json

router = Router()


class WorkoutStates(StatesGroup):
    choosing_workout_type = State()
    choosing_muscle_group = State()
    viewing_exercises = State()
    generating_plan = State()


@router.message(Command("workouts"))
async def workouts_command(message: types.Message):
    """Команда тренировок"""
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
        [InlineKeyboardButton(text="🏠 Домашние тренировки", callback_data="workout_type:bodyweight")],
        [InlineKeyboardButton(text="🏢 Сплит-тренировки", callback_data="workout_type:split")],
        [InlineKeyboardButton(text="🎯 Персональный план", callback_data="workout_type:personal")],
        [InlineKeyboardButton(text="💪 По группам мышц", callback_data="workout_type:muscle_groups")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "workouts")
async def workouts_callback(callback: types.CallbackQuery):
    """Обработка кнопки тренировок из личного кабинета"""
    await show_workouts_menu(callback.message)
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


@router.callback_query(lambda c: c.data == "workout_type:personal")
async def personal_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Персональный план тренировок"""
    await state.set_state(WorkoutStates.generating_plan)
    
    user = await get_user_by_tg_id(callback.from_user.id)
    if not user:
        await callback.answer("Пользователь не найден")
        return
    
    # Генерируем персональный план
    plan = generate_week_plan(
        user.level.value if user.level else 'beginner',
        user.weight_kg or 70,
        user.height_cm or 170,
        user.gender or 'male',
        user.age or 25
    )
    
    text = (
        f"🎯 <b>Персональный план тренировок</b>\n\n"
        f"Уровень: <b>{user.level.value.title() if user.level else 'Beginner'}</b>\n"
        f"Вес: <b>{user.weight_kg or 70} кг</b>\n"
        f"Рост: <b>{user.height_cm or 170} см</b>\n\n"
        "Ваш план на неделю:"
    )
    
    kb_buttons = []
    for day, exercises in plan.items():
        text += f"\n<b>{day.title()}:</b>\n"
        for exercise in exercises[:3]:  # Показываем первые 3 упражнения
            text += f"• {exercise['name']}\n"
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"📋 {day.title()}", 
                callback_data=f"personal_day:{day}"
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
    
    exercises = get_bodyweight_exercises(muscle_group)
    
    text = f"🏠 <b>Домашние упражнения: {muscle_group.title()}</b>\n\n"
    
    kb_buttons = []
    for level, level_exercises in exercises.items():
        text += f"<b>{level.title()}:</b>\n"
        for i, exercise in enumerate(level_exercises[:3]):  # Показываем первые 3
            text += f"• {exercise['name']}\n"
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🎥 {level.title()} упражнения", 
                callback_data=f"show_bodyweight_exercises:{muscle_group}:{level}"
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
    level = user.level.value if user and user.level else 'beginner'
    
    exercises = get_exercises_for_muscle_group(muscle_group, level)
    
    text = f"💪 <b>Упражнения: {muscle_group.title()}</b>\n\n"
    text += f"Уровень: <b>{level.title()}</b>\n\n"
    
    kb_buttons = []
    for i, exercise in enumerate(exercises[:5]):  # Показываем первые 5 упражнений
        text += f"{i+1}. {exercise['name']}\n"
        
        kb_buttons.append([
            InlineKeyboardButton(
                text=f"🎥 {exercise['name']}", 
                callback_data=f"show_exercise_videos:{muscle_group}:{level}:{exercise['name']}"
            )
        ])
    
    kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:muscle_groups")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("show_exercise_videos:"))
async def show_exercise_video(callback: types.CallbackQuery):
    """Показать видео упражнения"""
    parts = callback.data.split(":")
    muscle_group = parts[1]
    level = parts[2]
    exercise_name = parts[3]
    
    # Отправляем видео или описание упражнения
    await send_exercise_demo(
        callback.message,
        exercise_name,
        muscle_group,
        level,
        "Правильная техника выполнения упражнения"
    )
    
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
        text += f"• <b>{day}:</b> {', '.join(muscles)}\n"
    
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