from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, func
from app.db.session import get_session_maker
from app.db.models import User, Purchase

router = Router()


@router.message(Command("admin"))
async def admin_stats(message: types.Message):
	async_session = get_session_maker()
	async with async_session() as session:
		users_count = (await session.execute(select(func.count()).select_from(User))).scalar_one()
		purchases_count = (await session.execute(select(func.count()).select_from(Purchase))).scalar_one()
	await message.answer(f"Пользователей: {users_count}\nПокупок: {purchases_count}")