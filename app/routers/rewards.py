from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.rewards_utils import rewards_manager, motivation_manager, progress_tracker
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access, add_stars_to_user, get_user_stars
from app.utils.chat_cleanup import cleanup_rewards_messages
from app.db.models import ProgramLevel
import json

router = Router()


class RewardsStates(StatesGroup):
	choosing_action = State()
	viewing_prizes = State()
	exchanging_stars = State()
	uploading_progress_photo = State()


@router.message(Command("rewards"))
async def rewards_command(message: types.Message):
	"""Команда наград"""
	await show_rewards_menu(message)


async def show_rewards_menu(message: types.Message):
	"""Показать главное меню наград"""
	# Проверяем доступ пользователя
	if not await user_has_paid_access(message.from_user.id):
		await message.answer("❌ Для доступа к системе наград необходимо приобрести программу.")
		return
	
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
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
		[InlineKeyboardButton(text="📸 Загрузить фото прогресса", callback_data="upload_progress_photo")],
		[InlineKeyboardButton(text="🔗 Пригласить друга", callback_data="invite_friend")],
		[InlineKeyboardButton(text="🏅 Ежемесячный розыгрыш", callback_data="monthly_raffle")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_rewards")
async def cabinet_rewards_callback(callback: types.CallbackQuery):
	"""Обработка кнопки наград из личного кабинета"""
	await show_rewards_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "available_prizes")
async def available_prizes(callback: types.CallbackQuery, state: FSMContext):
	"""Показать доступные призы"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	prizes = await rewards_manager.get_available_prizes()
	
	text = f"🎁 <b>Доступные призы</b>\n\nВаши звезды: <b>{user.stars} ⭐</b>\n\n"
	
	kb_buttons = []
	for prize in prizes:
		can_afford = user.stars >= prize['stars_required']
		status = "✅ Доступно" if can_afford else "❌ Недостаточно звезд"
		
		text += f"<b>{prize['title']}</b>\n"
		text += f"• {prize['description']}\n"
		text += f"• Стоимость: {prize['stars_required']} ⭐\n"
		text += f"• Статус: {status}\n\n"
		
		if can_afford:
			kb_buttons.append([
				InlineKeyboardButton(
					text=f"🎁 Обменять: {prize['title']}", 
					callback_data=f"redeem_prize:{prize['title']}:{prize['stars_required']}"
				)
			])
	
	kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")])
	kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("redeem_prize:"))
async def redeem_prize(callback: types.CallbackQuery, state: FSMContext):
	"""Обменять приз на звезды"""
	parts = callback.data.split(":")
	prize_title = parts[1]
	prize_stars = int(parts[2])
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	if user.stars < prize_stars:
		await callback.answer("Недостаточно звезд для обмена!", show_alert=True)
		return
	
	# Обмениваем приз
	success = await rewards_manager.redeem_prize(user.id, prize_title, prize_stars)
	
	if success:
		text = (
			f"🎁 <b>Приз обменян!</b>\n\n"
			f"Приз: {prize_title}\n"
			f"Стоимость: {prize_stars} ⭐\n"
			f"Остаток звезд: {user.stars - prize_stars} ⭐\n\n"
			f"Мы свяжемся с вами для доставки приза!"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="🎁 Другие призы", callback_data="available_prizes")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	else:
		await callback.answer("Ошибка при обмене приза!", show_alert=True)
	
	await callback.answer()


@router.callback_query(lambda c: c.data == "exchange_stars")
async def exchange_stars(callback: types.CallbackQuery, state: FSMContext):
	"""Обмен звезд"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"🏆 <b>Обмен звезд</b>\n\n"
		f"Ваши звезды: <b>{user.stars} ⭐</b>\n\n"
		"Выберите действие:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🎁 Обменять на призы", callback_data="available_prizes")],
		[InlineKeyboardButton(text="💰 Обменять на деньги", callback_data="exchange_for_money")],
		[InlineKeyboardButton(text="📊 История обменов", callback_data="exchange_history")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "exchange_for_money")
async def exchange_for_money(callback: types.CallbackQuery, state: FSMContext):
	"""Обмен звезд на деньги"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Курс обмена: 1 звезда = 10 рублей
	exchange_rate = 10
	available_money = user.stars * exchange_rate
	
	text = (
		f"💰 <b>Обмен звезд на деньги</b>\n\n"
		f"Ваши звезды: <b>{user.stars} ⭐</b>\n"
		f"Курс обмена: 1 звезда = {exchange_rate} ₽\n"
		f"Доступно к обмену: <b>{available_money} ₽</b>\n\n"
		"Минимальная сумма для вывода: 1000 ₽ (100 звезд)\n\n"
		"Выберите сумму для обмена:"
	)
	
	kb_buttons = []
	if user.stars >= 100:
		kb_buttons.append([InlineKeyboardButton(text="💳 Вывести 1000 ₽ (100 звезд)", callback_data="withdraw_money:1000:100")])
	if user.stars >= 200:
		kb_buttons.append([InlineKeyboardButton(text="💳 Вывести 2000 ₽ (200 звезд)", callback_data="withdraw_money:2000:200")])
	if user.stars >= 500:
		kb_buttons.append([InlineKeyboardButton(text="💳 Вывести 5000 ₽ (500 звезд)", callback_data="withdraw_money:5000:500")])
	
	kb_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="exchange_stars")])
	kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("withdraw_money:"))
async def withdraw_money(callback: types.CallbackQuery, state: FSMContext):
	"""Вывод денег"""
	parts = callback.data.split(":")
	money_amount = int(parts[1])
	stars_cost = int(parts[2])
	
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	if user.stars < stars_cost:
		await callback.answer("Недостаточно звезд!", show_alert=True)
		return
	
	# Обмениваем звезды на деньги
	success = await rewards_manager.redeem_prize(user.id, f"Вывод {money_amount} ₽", stars_cost)
	
	if success:
		text = (
			f"💰 <b>Заявка на вывод создана!</b>\n\n"
			f"Сумма: {money_amount} ₽\n"
			f"Списано звезд: {stars_cost} ⭐\n"
			f"Остаток звезд: {user.stars - stars_cost} ⭐\n\n"
			f"Мы обработаем вашу заявку в течение 24 часов.\n"
			f"Деньги будут переведены на указанную карту."
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="💰 Другие суммы", callback_data="exchange_for_money")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="exchange_stars")]
		])
		
		await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	else:
		await callback.answer("Ошибка при создании заявки!", show_alert=True)
	
	await callback.answer()


@router.callback_query(lambda c: c.data == "stars_history")
async def stars_history(callback: types.CallbackQuery, state: FSMContext):
	"""История звезд"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# В реальном проекте здесь должна быть логика получения истории из БД
	# Пока что показываем заглушку
	
	text = (
		f"📊 <b>История звезд</b>\n\n"
		"<b>Последние события:</b>\n"
		"• Регистрация: +10 ⭐\n"
		"• Первая тренировка: +5 ⭐\n"
		"• Загрузка фото прогресса: +3 ⭐\n"
		"• Обмен приза: -100 ⭐\n\n"
		"<b>Всего заработано:</b> {user.stars + 100} ⭐\n"
		"<b>Всего потрачено:</b> 100 ⭐\n"
		"<b>Текущий баланс:</b> {user.stars} ⭐"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Подробная статистика", callback_data="detailed_stats")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "upload_progress_photo")
async def upload_progress_photo(callback: types.CallbackQuery, state: FSMContext):
	"""Загрузка фото прогресса"""
	text = (
		"📸 <b>Загрузка фото прогресса</b>\n\n"
		"Отправьте фото для оценки прогресса.\n\n"
		"<b>Рекомендации:</b>\n"
		"• Сделайте фото спереди, сбоку и сзади\n"
		"• Укажите текущий вес\n"
		"• Фото должны быть в хорошем качестве\n\n"
		"<b>Награда:</b> 1-5 звезд за прогресс\n\n"
		"Отправьте фото или нажмите 'Назад'"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(RewardsStates.uploading_progress_photo)
	await callback.answer()


@router.message(RewardsStates.uploading_progress_photo, F.photo)
async def process_progress_photo(message: types.Message, state: FSMContext):
	"""Обработка фото прогресса"""
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
		await state.clear()
		return
	
	# Сохраняем фото
	photo_file_id = message.photo[-1].file_id
	
	# В реальном проекте здесь должна быть логика сохранения в БД
	# await save_progress_photo(user.id, photo_file_id)
	
	# Оцениваем прогресс и награждаем звездами
	stars_earned = await progress_tracker.award_stars_for_progress(user.id, "Загрузка фото прогресса")
	
	text = (
		f"📸 <b>Фото прогресса загружено!</b>\n\n"
		f"Спасибо за фото! Мы оценим ваш прогресс.\n\n"
		f"<b>Награда:</b> +{stars_earned} ⭐\n"
		f"<b>Новый баланс:</b> {user.stars + stars_earned} ⭐\n\n"
		f"Продолжайте тренироваться и загружайте фото каждые 2-4 недели!"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Загрузить еще фото", callback_data="upload_progress_photo")],
		[InlineKeyboardButton(text="🎁 Обменять звезды", callback_data="available_prizes")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")
	await state.clear()


@router.callback_query(lambda c: c.data == "invite_friend")
async def invite_friend(callback: types.CallbackQuery, state: FSMContext):
	"""Пригласить друга"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
	
	text = (
		f"🔗 <b>Пригласить друга</b>\n\n"
		f"Пригласите друзей и получите бонусы!\n\n"
		f"<b>Ваша реферальная ссылка:</b>\n"
		f"<code>{referral_link}</code>\n\n"
		f"<b>Бонусы:</b>\n"
		f"• Вы: +100 звезд за каждого друга\n"
		f"• Друг: скидка 10% на программу\n\n"
		f"<b>Как это работает:</b>\n"
		f"1. Поделитесь ссылкой с другом\n"
		f"2. Друг переходит по ссылке\n"
		f"3. Друг получает скидку 10%\n"
		f"4. Вы получаете 100 звезд\n"
		f"5. Друг покупает программу\n"
		f"6. Вы получаете еще 100 звезд!"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📤 Поделиться ссылкой", callback_data="share_referral_link")],
		[InlineKeyboardButton(text="📊 Статистика рефералов", callback_data="referral_stats")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "share_referral_link")
async def share_referral_link(callback: types.CallbackQuery, state: FSMContext):
	"""Поделиться реферальной ссылкой"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
	
	text = (
		f"🔗 <b>Поделитесь ссылкой</b>\n\n"
		f"Скопируйте и отправьте эту ссылку друзьям:\n\n"
		f"<code>{referral_link}</code>\n\n"
		f"Или нажмите кнопку ниже для быстрого шаринга:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📤 Поделиться в Telegram", url=f"https://t.me/share/url?url={referral_link}&text=Привет! Я использую отличного фитнес-бота. Попробуй и получи скидку 10%!")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="invite_friend")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "referral_stats")
async def referral_stats(callback: types.CallbackQuery, state: FSMContext):
	"""Статистика рефералов"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# В реальном проекте здесь должна быть логика получения статистики из БД
	# Пока что показываем заглушку
	
	text = (
		f"📊 <b>Статистика рефералов</b>\n\n"
		f"<b>Общая статистика:</b>\n"
		f"• Всего приглашено: 0 друзей\n"
		f"• Активных рефералов: 0\n"
		f"• Заработано звезд: 0 ⭐\n\n"
		f"<b>Как увеличить:</b>\n"
		"• Поделитесь ссылкой в соцсетях\n"
		"• Расскажите друзьям о боте\n"
		"• Покажите свои результаты\n"
		"• Предложите тренироваться вместе"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔗 Пригласить друга", callback_data="invite_friend")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "monthly_raffle")
async def monthly_raffle(callback: types.CallbackQuery, state: FSMContext):
	"""Ежемесячный розыгрыш"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"🏅 <b>Ежемесячный розыгрыш призов</b>\n\n"
		f"<b>Как участвовать:</b>\n"
		"• Тренируйтесь и зарабатывайте звезды\n"
		"• Загружайте фото прогресса\n"
		"• Приглашайте друзей\n"
		"• Будьте активны в боте\n\n"
		f"<b>Призы:</b>\n"
		"• 1 место: Главный приз (определяется админом)\n"
		"• 2-5 места: Призы из каталога\n\n"
		"<b>Ваша позиция:</b> Не определено\n"
		"<b>Ваши звезды:</b> {user.stars} ⭐\n\n"
		f"<b>Следующий розыгрыш:</b> 1-го числа следующего месяца"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Топ участников", callback_data="top_participants")],
		[InlineKeyboardButton(text="🏆 Призы розыгрыша", callback_data="raffle_prizes")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "top_participants")
async def top_participants(callback: types.CallbackQuery, state: FSMContext):
	"""Топ участников розыгрыша"""
	text = (
		"📊 <b>Топ участников розыгрыша</b>\n\n"
		"<b>Текущий месяц:</b>\n\n"
		"🏆 1. @user1 - 1250 ⭐\n"
		"🥈 2. @user2 - 980 ⭐\n"
		"🥉 3. @user3 - 750 ⭐\n"
		"4. @user4 - 620 ⭐\n"
		"5. @user5 - 580 ⭐\n\n"
		"<b>Ваша позиция:</b> Не в топ-5\n"
		"<b>Ваши звезды:</b> 0 ⭐\n\n"
		"Продолжайте тренироваться и зарабатывать звезды!"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🏅 Ежемесячный розыгрыш", callback_data="monthly_raffle")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "raffle_prizes")
async def raffle_prizes(callback: types.CallbackQuery, state: FSMContext):
	"""Призы розыгрыша"""
	text = (
		"🏆 <b>Призы ежемесячного розыгрыша</b>\n\n"
		"<b>1 место - Главный приз:</b>\n"
		"• Умные часы Apple Watch\n"
		"• Или эквивалент в денежном выражении\n\n"
		"<b>2-5 места:</b>\n"
		"• Призы из каталога на выбор\n"
		"• Беспроводные наушники\n"
		"• Кроссовки для фитнеса\n"
		"• Протеиновый порошок\n"
		"• Денежные призы\n\n"
		"<b>Дополнительные призы:</b>\n"
		"• За активность в боте\n"
		"• За регулярные тренировки\n"
		"• За достижение целей"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🏅 Ежемесячный розыгрыш", callback_data="monthly_raffle")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "rewards")
async def back_to_rewards(callback: types.CallbackQuery):
	"""Возврат в главное меню наград"""
	await show_rewards_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "detailed_stats")
async def detailed_stats(callback: types.CallbackQuery, state: FSMContext):
	"""Подробная статистика"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"📊 <b>Подробная статистика</b>\n\n"
		f"<b>Общая информация:</b>\n"
		f"• Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n"
		f"• Всего звезд заработано: {user.stars + 100} ⭐\n"
		f"• Всего звезд потрачено: 100 ⭐\n"
		f"• Текущий баланс: {user.stars} ⭐\n\n"
		f"<b>Источники звезд:</b>\n"
		"• Регистрация: +10 ⭐\n"
		"• Первая тренировка: +5 ⭐\n"
		"• Загрузка фото: +3 ⭐\n"
		"• Достижение целей: +10 ⭐\n"
		"• Рефералы: +100 ⭐\n\n"
		f"<b>Расходы:</b>\n"
		"• Обмен призов: -100 ⭐\n\n"
		f"<b>Рекомендации:</b>\n"
		"• Тренируйтесь регулярно\n"
		"• Загружайте фото прогресса\n"
		"• Приглашайте друзей\n"
		"• Достигайте поставленных целей"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 История звезд", callback_data="stars_history")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "exchange_history")
async def exchange_history(callback: types.CallbackQuery, state: FSMContext):
	"""История обменов"""
	text = (
		"📊 <b>История обменов</b>\n\n"
		"<b>Последние обмены:</b>\n"
		"• 15.12.2024 - Обмен приза: Беспроводные наушники (-500 ⭐)\n"
		"• 10.12.2024 - Вывод денег: 1000 ₽ (-100 ⭐)\n"
		"• 05.12.2024 - Обмен приза: Протеиновый порошок (-200 ⭐)\n\n"
		"<b>Статистика обменов:</b>\n"
		"• Всего обменов: 3\n"
		"• Звезд потрачено: 800 ⭐\n"
		"• Получено призов: 2\n"
		"• Выведено денег: 1000 ₽"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🏆 Обменять звезды", callback_data="exchange_stars")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="rewards")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()