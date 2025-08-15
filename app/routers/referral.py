from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, update
from app.db.session import get_session_maker
from app.db.models import User, Referral
import secrets

router = Router()


def generate_ref_code() -> str:
	return secrets.token_urlsafe(6)


@router.message(Command("ref"))
async def ref_info(message: types.Message):
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
		if not user:
			await message.answer("Сначала выполните /start")
			return
		ref = (await session.execute(select(Referral).where(Referral.referrer_user_id == user.id))).scalar_one_or_none()
		if not ref:
			code = generate_ref_code()
			ref = Referral(referrer_user_id=user.id, referral_code=code)
			session.add(ref)
			await session.commit()
		link = f"t.me/{(await message.bot.me()).username}?start=ref_{ref.referral_code}"
		await message.answer(f"Ваша реферальная ссылка:\n{link}\nДруг получит скидку 10%. За каждого — +100 звёзд.")