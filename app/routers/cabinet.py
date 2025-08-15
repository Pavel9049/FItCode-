from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("cabinet"))
async def cabinet(message: types.Message):
	text = (
		"Личный кабинет:\n\n"
		"🎯 Цели и прогресс — /goals\n"
		"🏋️ Тренировки — /workouts\n"
		"🍲 Меню на неделю — /menu\n"
		"🎁 Подарки — /rewards\n"
		"💬 Поддержка (PRO) — /support\n"
		"⚙️ Настройки — /settings\n"
	)
	await message.answer(text)