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
    print(f"🏋️‍♂️ Получена команда workouts от пользователя {message.from_user.id}")
    try:
        await cleanup_workout_messages(message)
        await show_workouts_menu(message)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Error in workouts_command: {e}")


async def show_workouts_menu(message: types.Message):
    """Показать главное меню тренировок"""
    try:
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
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Error in show_workouts_menu: {e}")


@router.callback_query(lambda c: c.data == "workouts")
async def workouts_callback(callback: types.CallbackQuery):
    """Обработка кнопки тренировок из личного кабинета"""
    print(f"🏋️‍♂️ Получен callback workouts от пользователя {callback.from_user.id}")
    try:
        await cleanup_workout_messages(callback.message)
        await show_workouts_menu(callback.message)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in workouts_callback: {e}")


@router.callback_query(lambda c: c.data == "workout_type:personal")
async def personal_workouts(callback: types.CallbackQuery, state: FSMContext):
    """Персональный план тренировок"""
    print(f"🎯 Получен callback workout_type:personal от пользователя {callback.from_user.id}")
    try:
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
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in personal_workouts: {e}")


@router.callback_query(lambda c: c.data.startswith("goal:"))
async def goal_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор цели тренировок"""
    print(f"🎯 Получен callback goal от пользователя {callback.from_user.id}: {callback.data}")
    try:
        goal = callback.data.split(":")[1]
        await state.update_data(goal=goal)
        await state.set_state(WorkoutStates.choosing_equipment)
        
        text = (
            "🏋️‍♂️ <b>Выберите доступное оборудование</b>\n\n"
            "Отметьте все, что у вас есть:"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Без оборудования", callback_data="equipment:bodyweight")],
            [InlineKeyboardButton(text="🏋️‍♂️ Гантели", callback_data="equipment:dumbbells")],
            [InlineKeyboardButton(text="🏋️‍♂️ Штанга", callback_data="equipment:barbell")],
            [InlineKeyboardButton(text="🏢 Тренажеры", callback_data="equipment:machines")],
            [InlineKeyboardButton(text="🎯 Все виды", callback_data="equipment:all")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:personal")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in goal_selected: {e}")


@router.callback_query(lambda c: c.data.startswith("equipment:"))
async def equipment_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор оборудования"""
    print(f"🏋️‍♂️ Получен callback equipment от пользователя {callback.from_user.id}: {callback.data}")
    try:
        equipment = callback.data.split(":")[1]
        user = await get_user_by_tg_id(callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        if equipment == "all":
            available_equipment = [e for e in EquipmentType]
        else:
            available_equipment = [EquipmentType(equipment)]
        
        data = await state.get_data()
        goal = WorkoutGoal(data.get("goal", "tone"))
        level = WorkoutLevel(user.level.value if user.level else "beginner")
        
        workout_plan = generate_workout_plan(
            user_weight=user.weight_kg or 70,
            user_height=user.height_cm or 170,
            user_gender=user.gender or "male",
            user_age=user.age or 25,
            goal=goal,
            level=level,
            available_equipment=available_equipment
        )
        
        await state.update_data(workout_plan=workout_plan)
        await state.set_state(WorkoutStates.generating_plan)
        
        await show_workout_plan(callback.message, workout_plan, goal, level)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in equipment_selected: {e}")


async def show_workout_plan(message: types.Message, workout_plan: dict, goal: WorkoutGoal, level: WorkoutLevel):
    """Показать план тренировок"""
    try:
        goal_names = {
            "lose_weight": "Похудение",
            "gain_mass": "Набор массы", 
            "cut": "Подсушивание",
            "tone": "Поддержание тонуса"
        }
        
        text = (
            f"🎯 <b>Ваш персональный план тренировок</b>\n\n"
            f"Цель: <b>{goal_names.get(goal.value, goal.value)}</b>\n"
            f"Уровень: <b>{level.value.title()}</b>\n\n"
            "Выберите день недели:"
        )
        
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        buttons = []
        
        for i, day in enumerate(days):
            day_key = f"day_{i+1}"
            if day_key in workout_plan and workout_plan[day_key].get("exercises"):
                buttons.append([InlineKeyboardButton(
                    text=f"📅 {day} ({len(workout_plan[day_key]['exercises'])} упражнений)", 
                    callback_data=f"show_day_workout:{day_key}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text=f"📅 {day} (отдых)", 
                    callback_data=f"show_day_workout:{day_key}"
                )])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:personal")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Error in show_workout_plan: {e}")


@router.callback_query(lambda c: c.data.startswith("show_day_workout:"))
async def show_day_workout(callback: types.CallbackQuery, state: FSMContext):
    """Показать тренировку на конкретный день"""
    print(f"📅 Получен callback show_day_workout от пользователя {callback.from_user.id}: {callback.data}")
    try:
        day = callback.data.split(":")[1]
        data = await state.get_data()
        workout_plan = data.get("workout_plan", {})
        
        if day not in workout_plan:
            await callback.answer("День не найден в плане тренировок")
            return
        
        day_plan = workout_plan[day]
        if not day_plan.get("exercises"):
            await callback.message.edit_text(
                f"📅 <b>День отдыха</b>\n\n"
                f"Сегодня день восстановления. Отдохните и подготовьтесь к следующей тренировке!",
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        # Отправляем план тренировки с медиа
        success = await send_workout_plan_with_media(callback.message, workout_plan, day)
        if not success:
            # Если медиа нет, показываем текстовый план
            text = f"📅 <b>План тренировки</b>\n\n"
            for i, exercise in enumerate(day_plan["exercises"], 1):
                text += (
                    f"{i}. <b>{exercise['name']}</b>\n"
                    f"🎯 {', '.join(exercise['target_muscles'])}\n"
                    f"⚖️ {exercise['sets']} x {exercise['reps']} @ {exercise['weight']}кг\n"
                    f"⏱️ Отдых: {exercise['rest_time']} сек\n\n"
                )
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к плану", callback_data="back_to_workout_plan")]
            ])
            
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in show_day_workout: {e}")


@router.callback_query(lambda c: c.data == "back_to_workout_plan")
async def back_to_workout_plan(callback: types.CallbackQuery, state: FSMContext):
    """Возврат к плану тренировок"""
    print(f"🔙 Получен callback back_to_workout_plan от пользователя {callback.from_user.id}")
    try:
        data = await state.get_data()
        workout_plan = data.get("workout_plan", {})
        goal = WorkoutGoal(data.get("goal", "tone"))
        level = WorkoutLevel(data.get("level", "beginner"))
        
        await show_workout_plan(callback.message, workout_plan, goal, level)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in back_to_workout_plan: {e}")


@router.callback_query(lambda c: c.data == "workout_type:bodyweight")
async def bodyweight_workouts(callback: types.CallbackQuery):
    """Домашние тренировки без оборудования"""
    print(f"🏠 Получен callback workout_type:bodyweight от пользователя {callback.from_user.id}")
    try:
        text = (
            "🏠 <b>Домашние тренировки</b>\n\n"
            "Тренировки без специального оборудования. Выберите группу мышц:"
        )
        
        muscle_groups = get_muscle_groups()
        buttons = []
        
        for group in muscle_groups:
            group_names = {
                "chest": "Грудные мышцы",
                "back": "Спина", 
                "legs": "Ноги",
                "shoulders": "Плечи",
                "biceps": "Бицепс",
                "triceps": "Трицепс",
                "abs": "Пресс"
            }
            buttons.append([InlineKeyboardButton(
                text=f"💪 {group_names.get(group, group)}", 
                callback_data=f"bodyweight_muscle:{group}"
            )])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in bodyweight_workouts: {e}")


@router.callback_query(lambda c: c.data.startswith("bodyweight_muscle:"))
async def bodyweight_muscle_selected(callback: types.CallbackQuery):
    """Выбор группы мышц для домашних тренировок"""
    print(f"💪 Получен callback bodyweight_muscle от пользователя {callback.from_user.id}: {callback.data}")
    try:
        muscle_group = callback.data.split(":")[1]
        exercises = get_exercises_for_muscle_group(muscle_group, WorkoutLevel.BEGINNER)
        
        if not exercises:
            await callback.answer("Упражнения не найдены")
            return
        
        text = f"💪 <b>Упражнения для {muscle_group}</b>\n\n"
        
        buttons = []
        for i, exercise in enumerate(exercises[:5], 1):  # Показываем первые 5 упражнений
            text += (
                f"{i}. <b>{exercise.name}</b>\n"
                f"🎯 {', '.join(exercise.target_muscles)}\n"
                f"⚖️ {exercise.sets_range[0]}-{exercise.sets_range[1]} x {exercise.reps_range[0]}-{exercise.reps_range[1]}\n"
                f"⏱️ Отдых: {exercise.rest_time} сек\n\n"
            )
            buttons.append([InlineKeyboardButton(
                text=f"🎥 {exercise.name}", 
                callback_data=f"show_exercise_video:{exercise.name}:{muscle_group}"
            )])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:bodyweight")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in bodyweight_muscle_selected: {e}")


@router.callback_query(lambda c: c.data.startswith("show_exercise_video:"))
async def show_exercise_video(callback: types.CallbackQuery):
    """Показать видео упражнения"""
    print(f"🎥 Получен callback show_exercise_video от пользователя {callback.from_user.id}: {callback.data}")
    try:
        parts = callback.data.split(":")
        exercise_name = parts[1]
        muscle_group = parts[2]
        
        # Отправляем демо упражнения
        success = await send_exercise_demo(callback.message, exercise_name, muscle_group)
        
        if not success:
            await callback.answer("Видео не найдено")
        else:
            await callback.answer("Видео отправлено")
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in show_exercise_video: {e}")


@router.callback_query(lambda c: c.data == "workout_type:split")
async def split_workouts(callback: types.CallbackQuery):
    """Сплит-тренировки"""
    print(f"🏢 Получен callback workout_type:split от пользователя {callback.from_user.id}")
    try:
        text = (
            "🏢 <b>Сплит-тренировки</b>\n\n"
            "Выберите тип сплита:"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💪 Push/Pull/Legs", callback_data="split:ppl")],
            [InlineKeyboardButton(text="⬆️ Upper/Lower", callback_data="split:upper_lower")],
            [InlineKeyboardButton(text="🏋️‍♂️ Bro Split", callback_data="split:bro")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in split_workouts: {e}")


@router.callback_query(lambda c: c.data.startswith("split:"))
async def split_selected(callback: types.CallbackQuery):
    """Выбор сплита"""
    print(f"🏢 Получен callback split от пользователя {callback.from_user.id}: {callback.data}")
    try:
        split_type = callback.data.split(":")[1]
        split_info = get_split_info(split_type)
        
        text = f"🏢 <b>{split_info['name']}</b>\n\n{split_info['description']}\n\n"
        
        buttons = []
        for i, day in enumerate(split_info['days'], 1):
            buttons.append([InlineKeyboardButton(
                text=f"📅 День {i}: {day['name']}", 
                callback_data=f"split_day:{split_type}:{i}"
            )])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:split")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in split_selected: {e}")


@router.callback_query(lambda c: c.data == "workout_type:muscle_groups")
async def muscle_groups_workouts(callback: types.CallbackQuery):
    """Тренировки по группам мышц"""
    print(f"💪 Получен callback workout_type:muscle_groups от пользователя {callback.from_user.id}")
    try:
        text = (
            "💪 <b>Тренировки по группам мышц</b>\n\n"
            "Выберите группу мышц:"
        )
        
        muscle_groups = get_muscle_groups()
        buttons = []
        
        for group in muscle_groups:
            group_names = {
                "chest": "Грудные мышцы",
                "back": "Спина", 
                "legs": "Ноги",
                "shoulders": "Плечи",
                "biceps": "Бицепс",
                "triceps": "Трицепс",
                "abs": "Пресс"
            }
            buttons.append([InlineKeyboardButton(
                text=f"💪 {group_names.get(group, group)}", 
                callback_data=f"muscle_group:{group}"
            )])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workouts")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in muscle_groups_workouts: {e}")


@router.callback_query(lambda c: c.data.startswith("muscle_group:"))
async def muscle_group_selected(callback: types.CallbackQuery):
    """Выбор группы мышц"""
    print(f"💪 Получен callback muscle_group от пользователя {callback.from_user.id}: {callback.data}")
    try:
        muscle_group = callback.data.split(":")[1]
        exercises = get_exercises_for_muscle_group(muscle_group, WorkoutLevel.BEGINNER)
        
        if not exercises:
            await callback.answer("Упражнения не найдены")
            return
        
        text = f"💪 <b>Упражнения для {muscle_group}</b>\n\n"
        
        buttons = []
        for i, exercise in enumerate(exercises[:5], 1):  # Показываем первые 5 упражнений
            text += (
                f"{i}. <b>{exercise.name}</b>\n"
                f"🎯 {', '.join(exercise.target_muscles)}\n"
                f"⚖️ {exercise.sets_range[0]}-{exercise.sets_range[1]} x {exercise.reps_range[0]}-{exercise.reps_range[1]}\n"
                f"⏱️ Отдых: {exercise.rest_time} сек\n\n"
            )
            buttons.append([InlineKeyboardButton(
                text=f"🎥 {exercise.name}", 
                callback_data=f"show_exercise_video:{exercise.name}:{muscle_group}"
            )])
        
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="workout_type:muscle_groups")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in muscle_group_selected: {e}")