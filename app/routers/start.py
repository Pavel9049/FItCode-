from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from app.services.programs import get_paid_programs
from app.db.models import User, Referral
from app.db.session import get_session_maker
from sqlalchemy import select
import re

router = Router()


@router.message(CommandStart())
async def on_start(message: types.Message):
	# Проверяем реферальную ссылку
	start_param = message.text.split()[1] if len(message.text.split()) > 1 else None
	referrer_id = None
	
	if start_param and start_param.startswith('ref'):
		referrer_id = int(start_param[3:])  # Убираем 'ref' и получаем ID
	
	# Создаем или получаем пользователя
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == message.from_user.id)
		)).scalar_one_or_none()
		
		if not user:
			# Создаем нового пользователя
			user = User(
				tg_user_id=message.from_user.id,
				first_name=message.from_user.first_name,
				last_name=message.from_user.last_name,
				username=message.from_user.username
			)
			s.add(user)
			await s.commit()
			await s.refresh(user)
			
			# Если есть реферальная ссылка, создаем запись
			if referrer_id:
				referral = Referral(
					referrer_user_id=referrer_id,
					referral_code=f"ref{referrer_id}",
					referred_user_id=user.id,
					discount_percent=10
				)
				s.add(referral)
				await s.commit()
		
		elif referrer_id and user.id != referrer_id:
			# Проверяем, не регистрировался ли уже пользователь по реферальной ссылке
			existing_referral = (await s.execute(
				select(Referral).where(Referral.referred_user_id == user.id)
			)).scalar_one_or_none()
			
			if not existing_referral:
				referral = Referral(
					referrer_user_id=referrer_id,
					referral_code=f"ref{referrer_id}",
					referred_user_id=user.id,
					discount_percent=10
				)
				s.add(referral)
				await s.commit()

	text = (
		"Привет! Я — твой личный фитнес‑тренер и нутрициолог в одном лице.\n\n"
		"Здесь ты найдёшь:\n"
		"✅ Уникальные тренировки под каждый уровень\n"
		"✅ Персональное питание с КБЖУ и рецептами\n"
		"✅ Еженедельные обновления\n"
		"✅ Систему звёзд и реальных призов\n"
		"✅ Поддержку целей и фото-отчётов\n\n"
		"Почему мы?\n"
		"🔹 Упражнения не повторяются (кроме начальных уровней)\n"
		"🔹 Подбор под твою цель: похудеть, набрать массу, подсушиться, держать тонус\n"
		"🔹 Веса рассчитываются по росту и весу\n"
		"🔹 Видео-демонстрация каждого упражнения\n"
		"🔹 Тренировки дома и на улице — без инвентаря\n\n"
		"Выбери свою программу и начни уже сегодня!"
	)

	kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👉 Выбрать программу", callback_data="choose_program")]])

	# Если есть баннер в assets/banner.jpg — отправим, иначе просто текст
	try:
		banner = FSInputFile("assets/banner.jpg")
		await message.answer_photo(banner, caption=text, reply_markup=kb)
	except Exception:
		await message.answer(text, reply_markup=kb)


@router.callback_query(lambda c: c.data == "choose_program")
async def choose_program(callback: types.CallbackQuery):
	programs = get_paid_programs()
	
	# Проверяем, есть ли у пользователя реферальная скидка
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		discount = 0
		if user:
			referral = (await s.execute(
				select(Referral).where(Referral.referred_user_id == user.id)
			)).scalar_one_or_none()
			if referral:
				discount = referral.discount_percent
	
	lines = []
	for p in programs:
		original_price = p["price_rub"]
		discounted_price = int(original_price * (1 - discount / 100))
		
		features = "\n".join([f"• {f}" for f in p["features"]])
		
		if discount > 0:
			lines.append(f"{p['title']} — <s>{original_price}</s> <b>{discounted_price} ₽</b> (-{discount}%)\n{features}\n")
		else:
			lines.append(f"{p['title']} — {p['price_rub']} ₽\n{features}\n")
	
	text = "\n".join(lines)
	
	if discount > 0:
		text += f"\n🎉 <b>У вас скидка {discount}% по реферальной ссылке!</b>"

	# Кнопки покупки
	buttons = []
	for p in programs:
		original_price = p["price_rub"]
		discounted_price = int(original_price * (1 - discount / 100))
		
		if discount > 0:
			buttons.append([InlineKeyboardButton(
				text=f"Купить: {p['title']} ({discounted_price}₽)", 
				callback_data=f"buy:{p['code']}"
			)])
		else:
			buttons.append([InlineKeyboardButton(
				text=f"Купить: {p['title']} ({p['price_rub']}₽)", 
				callback_data=f"buy:{p['code']}"
			)])
	
	kb = InlineKeyboardMarkup(inline_keyboard=buttons)
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("buy:"))
async def buy_program(callback: types.CallbackQuery):
	"""Обработка покупки программы"""
	program_code = callback.data.split(":")[1]
	programs = get_paid_programs()
	selected_program = next((p for p in programs if p["code"] == program_code), None)
	
	if not selected_program:
		await callback.answer("Программа не найдена")
		return
	
	# Проверяем реферальную скидку
	async_session = get_session_maker()
	async with async_session() as s:
		user = (await s.execute(
			select(User).where(User.tg_user_id == callback.from_user.id)
		)).scalar_one_or_none()
		
		discount = 0
		if user:
			referral = (await s.execute(
				select(Referral).where(Referral.referred_user_id == user.id)
			)).scalar_one_or_none()
			if referral:
				discount = referral.discount_percent
	
	original_price = selected_program["price_rub"]
	final_price = int(original_price * (1 - discount / 100))
	
	text = (
		f"💳 <b>Оплата программы: {selected_program['title']}</b>\n\n"
		f"Цена: <b>{final_price} ₽</b>\n"
	)
	
	if discount > 0:
		text += f"Скидка: <b>{discount}%</b> (было {original_price} ₽)\n\n"
	
	text += "Выберите способ оплаты:"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💳 Банковская карта (ЮKassa)", callback_data=f"pay_yookassa:{program_code}")],
		[InlineKeyboardButton(text="💳 Международные карты (Stripe)", callback_data=f"pay_stripe:{program_code}")],
		[InlineKeyboardButton(text="⭐ Telegram Stars", callback_data=f"pay_stars:{program_code}")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="choose_program")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()