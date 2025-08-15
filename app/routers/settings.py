from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, update
from app.db.session import get_session_maker
from app.db.models import User

router = Router()


@router.message(Command("settings"))
async def settings_menu(message: types.Message):
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
		if not user:
			await message.answer("Сначала /start")
			return
		state = "включены" if user.notifications_enabled else "выключены"
		kb = types.InlineKeyboardMarkup(inline_keyboard=[
			[types.InlineKeyboardButton(text="Переключить уведомления", callback_data="notif:toggle")]
		])
		await message.answer(f"Уведомления сейчас {state}", reply_markup=kb)


@router.callback_query(lambda c: c.data == "notif:toggle")
async def notif_toggle(callback: types.CallbackQuery):
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		if not user:
			await callback.answer("Сначала /start", show_alert=True)
			return
		await s.execute(update(User).where(User.id == user.id).values(notifications_enabled=not user.notifications_enabled))
		await s.commit()
	await callback.message.edit_text("Готово. Зайдите снова в /settings")
	await callback.answer()