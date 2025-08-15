from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy import select
from app.db.session import get_session_maker
from app.db.models import Purchase, User, ProgramLevel
from app.utils.chat_cleanup import cleanup_cabinet_messages

router = Router()


@router.message(Command("cabinet"))
async def cabinet(message: types.Message):
	await cleanup_cabinet_messages(message)
	await show_cabinet(message)


async def show_cabinet(message: types.Message):
	"""Показать личный кабинет"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
		paid = False
		level = None
		if user:
			p = (await session.execute(select(Purchase).where(Purchase.user_id == user.id, Purchase.paid == True))).first()
			paid = bool(p)
			level = user.level

	if not paid:
		await message.answer("❌ Доступ к личному кабинету открывается после оплаты.\n\nВыберите программу в /start")
		return

	level_text = f"Уровень: <b>{level.value.title()}</b>" if level else "Уровень не выбран"
	
	text = (
		f"🏠 <b>Личный кабинет</b>\n\n"
		f"{level_text}\n\n"
		"Выберите раздел:"
	)

	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🎯 Цели и прогресс", callback_data="cabinet_goals")],
		[InlineKeyboardButton(text="🏋️‍♂️ Тренировки", callback_data="workouts")],
		[InlineKeyboardButton(text="🍲 Меню на неделю", callback_data="cabinet_menu")],
		[InlineKeyboardButton(text="🎁 Звезды и призы", callback_data="cabinet_rewards")],
		[InlineKeyboardButton(text="💬 Поддержка (PRO)", callback_data="cabinet_support")],
		[InlineKeyboardButton(text="⚙️ Настройки", callback_data="cabinet_settings")],
		[InlineKeyboardButton(text="📊 Статистика", callback_data="cabinet_stats")],
		[InlineKeyboardButton(text="🔗 Реферальная ссылка", callback_data="cabinet_referral")]
	])

	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet")
async def cabinet_callback(callback: types.CallbackQuery):
	"""Обработка кнопки личного кабинета"""
	await cleanup_cabinet_messages(callback.message)
	await show_cabinet(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_cabinet")
async def back_to_cabinet_callback(callback: types.CallbackQuery):
	"""Возврат в личный кабинет"""
	await show_cabinet(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_goals")
async def cabinet_goals(callback: types.CallbackQuery):
	"""Цели и прогресс"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		text = (
			f"🎯 <b>Цели и прогресс</b>\n\n"
			f"Текущий вес: <b>{user.weight_kg} кг</b>\n"
			f"Рост: <b>{user.height_cm} см</b>\n"
			f"Звезды: <b>{user.stars} ⭐</b>\n\n"
			"Выберите действие:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="📝 Поставить новую цель", callback_data="set_new_goal")],
			[InlineKeyboardButton(text="📸 Загрузить фото прогресса", callback_data="upload_progress_photo")],
			[InlineKeyboardButton(text="📊 Посмотреть статистику", callback_data="view_progress_stats")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_menu")
async def cabinet_menu(callback: types.CallbackQuery):
	"""Меню на неделю"""
	text = (
		"🍲 <b>Меню на неделю</b>\n\n"
		"Выберите действие:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📋 Посмотреть меню", callback_data="view_weekly_menu")],
		[InlineKeyboardButton(text="📄 Скачать PDF", callback_data="download_menu_pdf")],
		[InlineKeyboardButton(text="🍽️ Персональное питание", callback_data="personal_nutrition")],
		[InlineKeyboardButton(text="🔍 Поиск блюд", callback_data="search_meals")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_rewards")
async def cabinet_rewards(callback: types.CallbackQuery):
	"""Звезды и призы"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		text = (
			f"🎁 <b>Звезды и призы</b>\n\n"
			f"Ваши звезды: <b>{user.stars} ⭐</b>\n\n"
			"Выберите действие:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🎁 Доступные призы", callback_data="available_prizes")],
			[InlineKeyboardButton(text="🏆 Обменять звезды", callback_data="exchange_stars")],
			[InlineKeyboardButton(text="📊 История звезд", callback_data="stars_history")],
			[InlineKeyboardButton(text="🔗 Пригласить друга", callback_data="invite_friend")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_support")
async def cabinet_support(callback: types.CallbackQuery):
	"""Поддержка"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		
		if not user or not user.has_pro_support:
			text = (
				"💬 <b>Поддержка</b>\n\n"
				"❌ Поддержка 24/7 доступна только для PRO-пользователей.\n\n"
				"Для получения поддержки обновите программу до PRO."
			)
			
			kb = InlineKeyboardMarkup(inline_keyboard=[
				[InlineKeyboardButton(text="💎 Обновить до PRO", callback_data="upgrade_to_pro")],
				[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
			])
		else:
			text = (
				"💬 <b>Поддержка 24/7</b>\n\n"
				"✅ У вас есть доступ к поддержке.\n\n"
				"Напишите ваш вопрос, и мы ответим в течение 24 часов."
			)
			
			kb = InlineKeyboardMarkup(inline_keyboard=[
				[InlineKeyboardButton(text="📝 Написать в поддержку", callback_data="write_to_support")],
				[InlineKeyboardButton(text="📋 Частые вопросы", callback_data="faq")],
				[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
			])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_settings")
async def cabinet_settings(callback: types.CallbackQuery):
	"""Настройки"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		notifications_status = "✅ Включены" if user.notifications_enabled else "❌ Отключены"
		
		text = (
			f"⚙️ <b>Настройки</b>\n\n"
			f"Уведомления: {notifications_status}\n\n"
			"Выберите настройку:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")],
			[InlineKeyboardButton(text="👤 Профиль", callback_data="edit_profile")],
			[InlineKeyboardButton(text="🎯 Цели", callback_data="edit_goals")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_stats")
async def cabinet_stats(callback: types.CallbackQuery):
	"""Статистика"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		text = (
			f"📊 <b>Статистика</b>\n\n"
			f"Дата регистрации: <b>{user.created_at.strftime('%d.%m.%Y')}</b>\n"
			f"Звезды: <b>{user.stars} ⭐</b>\n"
			f"Уровень: <b>{user.level.value.title() if user.level else 'Не выбран'}</b>\n\n"
			"Выберите статистику:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🏋️‍♂️ Тренировки", callback_data="workout_stats")],
			[InlineKeyboardButton(text="🍲 Питание", callback_data="nutrition_stats")],
			[InlineKeyboardButton(text="📈 Прогресс", callback_data="progress_stats")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()


@router.callback_query(lambda c: c.data == "cabinet_referral")
async def cabinet_referral(callback: types.CallbackQuery):
	"""Реферальная ссылка"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
		
		if not user:
			await callback.answer("Пользователь не найден")
			return
		
		referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
		
		text = (
			f"🔗 <b>Реферальная программа</b>\n\n"
			f"Пригласите друзей и получите бонусы!\n\n"
			f"<b>Ваша ссылка:</b>\n"
			f"<code>{referral_link}</code>\n\n"
			f"<b>Бонусы:</b>\n"
			f"• Вы: +100 звезд за каждого друга\n"
			f"• Друг: скидка 10% на программу\n\n"
			"Выберите действие:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="📤 Поделиться ссылкой", callback_data="share_referral_link")],
			[InlineKeyboardButton(text="📊 Статистика рефералов", callback_data="referral_stats")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
		await callback.answer()