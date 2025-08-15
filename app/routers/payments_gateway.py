from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, update
from app.db.session import get_session_maker
from app.db.models import Purchase
from app.services.payments import PaymentGateway

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("pay:"))
async def on_choose_gateway(callback: types.CallbackQuery):
	_, gateway, purchase_id = callback.data.split(":", 2)
	async_session = get_session_maker()
	async with async_session() as session:
		purchase = (await session.execute(select(Purchase).where(Purchase.id == int(purchase_id)))).scalar_one_or_none()
		if not purchase:
			await callback.answer("Покупка не найдена", show_alert=True)
			return

		link = await PaymentGateway.create_payment_link(gateway, purchase.amount_rub, f"Покупка #{purchase.id}", {"purchase_id": purchase.id})
		await session.execute(update(Purchase).where(Purchase.id == purchase.id).values(gateway=gateway, external_id=link))
		await session.commit()

	text = (
		f"Счёт создан через {gateway}.\n"
		"Оплатите по ссылке ниже. Доступ откроется автоматически после подтверждения.\n\n"
		f"{link}"
	)
	kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Проверить оплату", callback_data=f"check:{purchase.id}")]])
	await callback.message.edit_text(text, reply_markup=kb)
	await callback.answer()