from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from app.db.session import get_session_maker
from app.db.models import Program, Purchase, User
from sqlalchemy import select

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("buy:"))
async def on_buy(callback: types.CallbackQuery, state: FSMContext):
	code = callback.data.split(":", 1)[1]

	async_session = get_session_maker()
	async with async_session() as session:
		prog = (await session.execute(select(Program).where(Program.code == code))).scalar_one_or_none()
		if not prog:
			await callback.answer("Программа не найдена", show_alert=True)
			return

		# Обеспечим запись пользователя в БД
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		if not user:
			user = User(
				tg_user_id=callback.from_user.id,
				first_name=callback.from_user.first_name,
				last_name=callback.from_user.last_name,
				username=callback.from_user.username,
			)
			session.add(user)
			await session.flush()

		purchase = Purchase(
			user_id=user.id,
			program_id=prog.id,
			gateway="pending",
			external_id="pending",
			amount_rub=prog.price_rub,
			currency="RUB",
			paid=False,
		)
		session.add(purchase)
		await session.commit()

	text = (
		f"Вы выбрали: {prog.title} — {prog.price_rub} ₽\n\n"
		"Способ оплаты: выберите ниже. Доступ откроется автоматически после оплаты, пожизненно."
	)

	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="ЮKassa (карты)", callback_data=f"pay:yookassa:{purchase.id}")],
		[InlineKeyboardButton(text="СБП (ЮKassa)", callback_data=f"pay:sbp:{purchase.id}")],
		[InlineKeyboardButton(text="SberPay (ЮKassa)", callback_data=f"pay:sberpay:{purchase.id}")],
		[InlineKeyboardButton(text="Tinkoff", callback_data=f"pay:tinkoff:{purchase.id}")],
		[InlineKeyboardButton(text="Stripe (международные)", callback_data=f"pay:stripe:{purchase.id}")],
		[InlineKeyboardButton(text="Telegram Stars", callback_data=f"pay:stars:{purchase.id}")],
		[InlineKeyboardButton(text="Криптовалюта (NOWPayments)", callback_data=f"pay:crypto:{purchase.id}")],
	])

	await callback.message.edit_text(text, reply_markup=kb)
	await callback.answer()