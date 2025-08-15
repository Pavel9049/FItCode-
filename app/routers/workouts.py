from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, update
from app.db.session import get_session_maker
from app.db.models import User, WorkoutPlan, ProgramLevel
from app.services.workouts import generate_week_plan
import json

router = Router()


@router.message(Command("workouts"))
async def workouts_entry(message: types.Message):
	kb = types.InlineKeyboardMarkup(inline_keyboard=[
		[types.InlineKeyboardButton(text="Домашние (без инвентаря)", callback_data="w:noequip")],
		[types.InlineKeyboardButton(text="Сплиты (зал/инвентарь)", callback_data="w:equip")],
	])
	await message.answer("Выберите формат тренировок:", reply_markup=kb)


@router.callback_query(lambda c: c.data in ("w:noequip", "w:equip"))
async def workouts_generate(callback: types.CallbackQuery):
	use_equip = callback.data == "w:equip"
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		if not user:
			await callback.answer("Сначала /start", show_alert=True)
			return
		level = user.level or ProgramLevel.beginner
		plan = generate_week_plan(level, goal="custom", weight_kg=user.weight_kg, has_equipment=use_equip)
		wp = WorkoutPlan(user_id=user.id, week_start=json.loads(json.dumps(plan))["week_start"], data_json=json.dumps(plan, ensure_ascii=False))
		s.add(wp)
		await s.commit()
	await callback.message.edit_text("План на неделю сформирован. Откройте личный кабинет: /cabinet")
	await callback.answer()