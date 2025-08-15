from aiogram import Router, types
from sqlalchemy import select
from app.db.session import get_session_maker
from app.db.models import Purchase

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("check:"))
async def on_check(callback: types.CallbackQuery):
	purchase_id = int(callback.data.split(":", 1)[1])
	async_session = get_session_maker()
	async with async_session() as session:
		p = (await session.execute(select(Purchase).where(Purchase.id == purchase_id))).scalar_one_or_none()
		if not p:
			await callback.answer("Покупка не найдена", show_alert=True)
			return
		if p.paid:
			await callback.message.edit_text("Оплата подтверждена! Доступ открыт навсегда. Перейдите в личный кабинет: /cabinet")
		else:
			await callback.answer("Платёж ещё не подтверждён. Попробуйте позже.", show_alert=True)