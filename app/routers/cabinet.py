from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select
from app.db.session import get_session_maker
from app.db.models import Purchase, User

router = Router()


@router.message(Command("cabinet"))
async def cabinet(message: types.Message):
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
		paid = False
		if user:
			p = (await session.execute(select(Purchase).where(Purchase.user_id == user.id, Purchase.paid == True))).first()
			paid = bool(p)

	if not paid:
		await message.answer("Доступ к личному кабинету открывается после оплаты. Выберите программу в /start")
		return

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