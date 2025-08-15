from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select
from app.db.session import get_session_maker
from app.db.models import User, Prize

router = Router()


@router.message(Command("rewards"))
async def rewards(message: types.Message):
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
		prizes = (await s.execute(select(Prize).where(Prize.is_active == True))).scalars().all()
	stars = user.stars if user else 0
	lines = [f"Ваши звёзды: {stars}", "\nДоступные призы:"]
	for p in prizes:
		lines.append(f"• {p.title} — {p.stars_required}⭐")
	await message.answer("\n".join(lines))