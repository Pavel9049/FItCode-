from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from app.db.session import get_session_maker
from app.db.models import Program, Purchase, User, Referral
from sqlalchemy import select
from app.services.programs import get_paid_programs

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("pay_yookassa:"))
async def pay_yookassa(callback: types.CallbackQuery, state: FSMContext):
	"""Оплата через ЮKassa"""
	program_code = callback.data.split(":", 1)[1]
	await process_payment(callback, "yookassa", program_code)


@router.callback_query(lambda c: c.data and c.data.startswith("pay_stripe:"))
async def pay_stripe(callback: types.CallbackQuery, state: FSMContext):
	"""Оплата через Stripe"""
	program_code = callback.data.split(":", 1)[1]
	await process_payment(callback, "stripe", program_code)


@router.callback_query(lambda c: c.data and c.data.startswith("pay_stars:"))
async def pay_stars(callback: types.CallbackQuery, state: FSMContext):
	"""Оплата через Telegram Stars"""
	program_code = callback.data.split(":", 1)[1]
	await process_payment(callback, "stars", program_code)


async def process_payment(callback: types.CallbackQuery, gateway: str, program_code: str):
	"""Обработка платежа"""
	programs = get_paid_programs()
	selected_program = next((p for p in programs if p["code"] == program_code), None)
	
	if not selected_program:
		await callback.answer("Программа не найдена", show_alert=True)
		return

	async_session = get_session_maker()
	async with async_session() as session:
		# Получаем или создаем пользователя
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

		# Проверяем реферальную скидку
		discount = 0
		referral = (await session.execute(
			select(Referral).where(Referral.referred_user_id == user.id)
		)).scalar_one_or_none()
		if referral:
			discount = referral.discount_percent

		original_price = selected_program["price_rub"]
		final_price = int(original_price * (1 - discount / 100))

		# Создаем запись о покупке
		purchase = Purchase(
			user_id=user.id,
			program_id=1,  # Временно используем ID 1, в реальности нужно получать из БД
			gateway=gateway,
			external_id="pending",
			amount_rub=final_price,
			currency="RUB",
			paid=False,
		)
		session.add(purchase)
		await session.commit()

		# Показываем информацию о платеже
		text = (
			f"💳 <b>Оплата через {get_gateway_name(gateway)}</b>\n\n"
			f"Программа: <b>{selected_program['title']}</b>\n"
			f"Сумма: <b>{final_price} ₽</b>\n"
		)
		
		if discount > 0:
			text += f"Скидка: <b>{discount}%</b> (было {original_price} ₽)\n"
		
		text += f"\nID покупки: <code>{purchase.id}</code>\n\n"
		
		if gateway == "yookassa":
			text += "Нажмите кнопку ниже для перехода к оплате:"
		elif gateway == "stripe":
			text += "Нажмите кнопку ниже для перехода к оплате:"
		elif gateway == "stars":
			text += "Нажмите кнопку ниже для оплаты через Telegram Stars:"
		else:
			text += "Нажмите кнопку ниже для оплаты:"

		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text=f"💳 Оплатить {final_price} ₽", callback_data=f"process_payment:{gateway}:{purchase.id}")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data=f"buy:{program_code}")]
		])

		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


def get_gateway_name(gateway: str) -> str:
	"""Получить название платежного шлюза"""
	names = {
		"yookassa": "ЮKassa (карты РФ)",
		"stripe": "Stripe (международные карты)",
		"stars": "Telegram Stars",
		"crypto": "Криптовалюта",
		"tinkoff": "Tinkoff",
		"sbp": "СБП"
	}
	return names.get(gateway, gateway.title())


@router.callback_query(lambda c: c.data and c.data.startswith("process_payment:"))
async def process_payment_callback(callback: types.CallbackQuery, state: FSMContext):
	"""Обработка нажатия на кнопку оплаты"""
	parts = callback.data.split(":")
	gateway = parts[1]
	purchase_id = int(parts[2])
	
	# Здесь должна быть логика создания платежа в соответствующем шлюзе
	# Пока что просто показываем сообщение
	
	text = (
		f"🔄 <b>Создание платежа...</b>\n\n"
		f"Платежный шлюз: {get_gateway_name(gateway)}\n"
		f"ID покупки: {purchase_id}\n\n"
		"⏳ Пожалуйста, подождите..."
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔄 Обновить статус", callback_data=f"check_payment:{purchase_id}")],
		[InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_payment")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("check_payment:"))
async def check_payment(callback: types.CallbackQuery, state: FSMContext):
	"""Проверка статуса платежа"""
	purchase_id = int(callback.data.split(":")[1])
	
	async_session = get_session_maker()
	async with async_session() as session:
		purchase = (await session.execute(
			select(Purchase).where(Purchase.id == purchase_id)
		)).scalar_one_or_none()
		
		if not purchase:
			await callback.answer("Покупка не найдена", show_alert=True)
			return
		
		if purchase.paid:
			text = (
				"✅ <b>Оплата прошла успешно!</b>\n\n"
				"Доступ к программе открыт.\n"
				"Теперь вы можете использовать все функции бота.\n\n"
				"Нажмите кнопку ниже, чтобы перейти в личный кабинет:"
			)
			
			kb = InlineKeyboardMarkup(inline_keyboard=[
				[InlineKeyboardButton(text="🏠 Личный кабинет", callback_data="cabinet")],
				[InlineKeyboardButton(text="🏋️‍♂️ Тренировки", callback_data="workouts")]
			])
			
			await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		else:
			text = (
				"⏳ <b>Оплата в обработке</b>\n\n"
				"Платеж еще не поступил.\n"
				"Попробуйте проверить статус через несколько минут.\n\n"
				f"ID покупки: {purchase_id}"
			)
			
			kb = InlineKeyboardMarkup(inline_keyboard=[
				[InlineKeyboardButton(text="🔄 Проверить снова", callback_data=f"check_payment:{purchase_id}")],
				[InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_payment")]
			])
			
			await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	
	await callback.answer()


@router.callback_query(lambda c: c.data == "cancel_payment")
async def cancel_payment(callback: types.CallbackQuery, state: FSMContext):
	"""Отмена платежа"""
	text = (
		"❌ <b>Платеж отменен</b>\n\n"
		"Вы можете попробовать оплатить позже.\n"
		"Нажмите кнопку ниже, чтобы выбрать программу:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="👉 Выбрать программу", callback_data="choose_program")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="start")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()