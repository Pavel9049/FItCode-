from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select
from app.db.session import get_session_maker
from app.db.models import User
from app.config import settings

router = Router()


@router.message(Command("support"))
async def support_entry(message: types.Message):
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
	if not user or not user.has_pro_support or not settings.support_chat_id:
		await message.answer("Поддержка 24/7 доступна в пакете Профессионал.")
		return
	await message.answer("Опишите вопрос. Я перешлю его тренеру.")


@router.message(lambda m: m.reply_to_message and "перешлю его тренеру" in (m.reply_to_message.text or ""))
async def support_forward(message: types.Message):
	if not settings.support_chat_id:
		return
	await message.bot.send_message(settings.support_chat_id, f"Вопрос от @{message.from_user.username or message.from_user.id}:\n{message.text}")
	await message.answer("Отправлено. Ожидайте ответ.")