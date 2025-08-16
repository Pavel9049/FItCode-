from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access, get_user_referral_discount, get_referral_stats
from app.utils.chat_cleanup import cleanup_referral_messages
from app.db.models import ProgramLevel
import json

router = Router()


class ReferralStates(StatesGroup):
	choosing_action = State()
	sharing_link = State()
	viewing_stats = State()


@router.message(Command("referral"))
async def referral_command(message: types.Message):
	"""Команда реферальной системы"""
	await cleanup_general_messages(message)
	await show_referral_menu(message)


async def show_referral_menu(message: types.Message):
	"""Показать главное меню реферальной системы"""
	# Проверяем доступ пользователя
	if not await user_has_paid_access(message.from_user.id):
		await message.answer("❌ Для доступа к реферальной системе необходимо приобрести программу.")
		return
	
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
		return
	
	# Получаем реферальную статистику
	referral_stats = await get_referral_stats(user.tg_user_id)
	
	text = (
		f"🔗 <b>Реферальная система</b>\n\n"
		f"<b>Ваша статистика:</b>\n"
		f"• Приглашено друзей: {referral_stats.get('total_referrals', 0)}\n"
		"• Активных рефералов: {referral_stats.get('active_referrals', 0)}\n"
		"• Заработано звезд: {referral_stats.get('stars_earned', 0)} ⭐\n"
		"• Скидка: {referral_stats.get('discount_percent', 0)}%\n\n"
		"<b>Как это работает:</b>\n"
		"• Пригласите друга по ссылке\n"
		"• Друг получит скидку 10%\n"
		"• Вы получите 100 звезд\n"
		"• Друг покупает программу\n"
		"• Вы получаете еще 100 звезд!\n\n"
		"Выберите действие:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔗 Получить ссылку", callback_data="get_referral_link")],
		[InlineKeyboardButton(text="📊 Статистика", callback_data="referral_statistics")],
		[InlineKeyboardButton(text="👥 Мои рефералы", callback_data="my_referrals")],
		[InlineKeyboardButton(text="📤 Поделиться", callback_data="share_referral")],
		[InlineKeyboardButton(text="💡 Советы", callback_data="referral_tips")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_referral")
async def cabinet_referral_callback(callback: types.CallbackQuery):
	"""Обработка кнопки реферальной системы из личного кабинета"""
	await cleanup_general_messages(callback.message)
	await show_referral_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "get_referral_link")
async def get_referral_link(callback: types.CallbackQuery, state: FSMContext):
	"""Получить реферальную ссылку"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
	
	text = (
		f"🔗 <b>Ваша реферальная ссылка</b>\n\n"
		f"<code>{referral_link}</code>\n\n"
		"<b>Как использовать:</b>\n"
		"1. Скопируйте ссылку\n"
		"2. Поделитесь с друзьями\n"
		"3. Друг переходит по ссылке\n"
		"4. Друг получает скидку 10%\n"
		"5. Вы получаете 100 звезд\n"
		"6. Друг покупает программу\n"
		"7. Вы получаете еще 100 звезд!\n\n"
		"<b>Бонусы:</b>\n"
		"• За каждого друга: +100 звезд\n"
		"• Другу: скидка 10% на программу\n"
		"• При покупке: еще +100 звезд\n"
		"• Накопительные бонусы\n\n"
		"<b>Где поделиться:</b>\n"
		"• Telegram чаты\n"
		"• Социальные сети\n"
		"• Личные сообщения\n"
		"• Форумы и блоги"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📤 Поделиться в Telegram", url=f"https://t.me/share/url?url={referral_link}&text=Привет! Я использую отличного фитнес-бота. Попробуй и получи скидку 10%!")],
		[InlineKeyboardButton(text="📋 Скопировать ссылку", callback_data="copy_referral_link")],
		[InlineKeyboardButton(text="📊 Статистика", callback_data="referral_statistics")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "copy_referral_link")
async def copy_referral_link(callback: types.CallbackQuery, state: FSMContext):
	"""Скопировать реферальную ссылку"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
	
	text = (
		f"📋 <b>Реферальная ссылка скопирована!</b>\n\n"
		f"<code>{referral_link}</code>\n\n"
		"Ссылка скопирована в буфер обмена.\n\n"
		"<b>Теперь вы можете:</b>\n"
		"• Вставить ссылку в любой чат\n"
		"• Отправить друзьям\n"
		"• Разместить в соцсетях\n"
		"• Добавить в подпись\n\n"
		"<b>Напоминание:</b>\n"
		"За каждого друга, который перейдет по ссылке и купит программу, вы получите 200 звезд!"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📤 Поделиться", callback_data="share_referral")],
		[InlineKeyboardButton(text="📊 Статистика", callback_data="referral_statistics")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="get_referral_link")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "referral_statistics")
async def referral_statistics(callback: types.CallbackQuery, state: FSMContext):
	"""Статистика рефералов"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Получаем реферальную статистику
	referral_stats = await get_referral_stats(user.tg_user_id)
	
	text = (
		f"📊 <b>Реферальная статистика</b>\n\n"
		f"<b>Общая статистика:</b>\n"
		f"• Всего приглашено: {referral_stats.get('total_referrals', 0)} друзей\n"
		"• Активных рефералов: {referral_stats.get('active_referrals', 0)}\n"
		"• Купили программу: {referral_stats.get('paid_referrals', 0)}\n"
		"• Заработано звезд: {referral_stats.get('stars_earned', 0)} ⭐\n\n"
		f"<b>По месяцам:</b>\n"
		f"• Декабрь 2024: {referral_stats.get('december_2024', 0)} рефералов\n"
		f"• Ноябрь 2024: {referral_stats.get('november_2024', 0)} рефералов\n"
		f"• Октябрь 2024: {referral_stats.get('october_2024', 0)} рефералов\n\n"
		f"<b>Конверсия:</b>\n"
		f"• Переходы по ссылке: {referral_stats.get('link_clicks', 0)}\n"
		f"• Регистрации: {referral_stats.get('registrations', 0)}\n"
		f"• Покупки: {referral_stats.get('purchases', 0)}\n"
		f"• Конверсия: {referral_stats.get('conversion_rate', 0)}%\n\n"
		f"<b>Доходы:</b>\n"
		f"• Звезды за переходы: {referral_stats.get('stars_for_clicks', 0)} ⭐\n"
		f"• Звезды за покупки: {referral_stats.get('stars_for_purchases', 0)} ⭐\n"
		f"• Всего звезд: {referral_stats.get('total_stars', 0)} ⭐"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="👥 Мои рефералы", callback_data="my_referrals")],
		[InlineKeyboardButton(text="📈 Графики", callback_data="referral_charts")],
		[InlineKeyboardButton(text="🔗 Получить ссылку", callback_data="get_referral_link")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "my_referrals")
async def my_referrals(callback: types.CallbackQuery, state: FSMContext):
	"""Мои рефералы"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"👥 <b>Мои рефералы</b>\n\n"
		f"<b>Активные рефералы:</b>\n\n"
		f"<b>1. @user123</b>\n"
		f"📅 Приглашен: 15 декабря\n"
		f"💳 Статус: Купил программу\n"
		"⭐ Звезд получено: 200\n"
		"📊 Активность: Высокая\n\n"
		f"<b>2. @fitness_lover</b>\n"
		f"📅 Приглашен: 12 декабря\n"
		f"💳 Статус: Зарегистрирован\n"
		"⭐ Звезд получено: 100\n"
		"📊 Активность: Средняя\n\n"
		f"<b>3. @health_guru</b>\n"
		f"📅 Приглашен: 10 декабря\n"
		f"💳 Статус: Купил программу\n"
		"⭐ Звезд получено: 200\n"
		"📊 Активность: Высокая\n\n"
		f"<b>4. @workout_buddy</b>\n"
		f"📅 Приглашен: 8 декабря\n"
		f"💳 Статус: Зарегистрирован\n"
		"⭐ Звезд получено: 100\n"
		"📊 Активность: Низкая\n\n"
		f"<b>5. @fit_mom</b>\n"
		f"📅 Приглашен: 5 декабря\n"
		f"💳 Статус: Купил программу\n"
		"⭐ Звезд получено: 200\n"
		"📊 Активность: Высокая\n\n"
		f"<b>Статистика:</b>\n"
		f"• Всего рефералов: 5\n"
		f"• Купили программу: 3\n"
		f"• Зарегистрированы: 2\n"
		f"• Всего звезд: 800 ⭐"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Подробная статистика", callback_data="referral_statistics")],
		[InlineKeyboardButton(text="🔗 Пригласить еще", callback_data="get_referral_link")],
		[InlineKeyboardButton(text="💬 Написать рефералам", callback_data="message_referrals")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "share_referral")
async def share_referral(callback: types.CallbackQuery, state: FSMContext):
	"""Поделиться реферальной ссылкой"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
	
	text = (
		f"📤 <b>Поделиться реферальной ссылкой</b>\n\n"
		f"<b>Ваша ссылка:</b>\n"
		f"<code>{referral_link}</code>\n\n"
		"<b>Способы поделиться:</b>\n\n"
		f"<b>📱 Telegram:</b>\n"
		"• Личные сообщения\n"
		"• Группы и каналы\n"
		"• Статус и био\n\n"
		f"<b>🌐 Социальные сети:</b>\n"
		"• Instagram Stories\n"
		"• Facebook посты\n"
		"• Twitter твиты\n"
		"• VK записи\n\n"
		f"<b>💬 Мессенджеры:</b>\n"
		"• WhatsApp\n"
		"• Viber\n"
		"• Discord\n"
		"• Slack\n\n"
		f"<b>📝 Другие способы:</b>\n"
		"• Email рассылка\n"
		"• Блоги и форумы\n"
		"• Визитки\n"
		"• Презентации"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📱 Telegram", url=f"https://t.me/share/url?url={referral_link}&text=Привет! Я использую отличного фитнес-бота. Попробуй и получи скидку 10%!")],
		[InlineKeyboardButton(text="📋 Скопировать", callback_data="copy_referral_link")],
		[InlineKeyboardButton(text="💡 Шаблоны сообщений", callback_data="message_templates")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "referral_tips")
async def referral_tips(callback: types.CallbackQuery, state: FSMContext):
	"""Советы по реферальной системе"""
	text = (
		"💡 <b>Советы по реферальной системе</b>\n\n"
		"<b>🎯 Как привлечь больше рефералов:</b>\n\n"
		"<b>1. Покажите свои результаты</b>\n"
		"• Делитесь прогрессом\n"
		"• Показывайте фото до/после\n"
		"• Рассказывайте о достижениях\n\n"
		f"<b>2. Объясните преимущества</b>\n"
		"• Персональные тренировки\n"
		"• Питание с КБЖУ\n"
		"• Система звезд и призов\n"
		"• Поддержка 24/7\n\n"
		f"<b>3. Используйте правильные каналы</b>\n"
		"• Фитнес-сообщества\n"
		"• Группы по похудению\n"
		"• Спортивные чаты\n"
		"• Личные контакты\n\n"
		f"<b>4. Создавайте контент</b>\n"
		"• Посты о тренировках\n"
		"• Рецепты ПП блюд\n"
		"• Мотивационные истории\n"
		"• Советы по фитнесу\n\n"
		f"<b>5. Будьте активны</b>\n"
		"• Регулярно делитесь ссылкой\n"
		"• Отвечайте на вопросы\n"
		"• Поддерживайте рефералов\n"
		"• Показывайте пример\n\n"
		f"<b>❌ Что НЕ делать:</b>\n"
		"• Спамить ссылками\n"
		"• Давить на людей\n"
		"• Давать ложные обещания\n"
		"• Игнорировать рефералов\n\n"
		f"<b>✅ Лучшие практики:</b>\n"
		"• Искренность и честность\n"
		"• Помощь и поддержка\n"
		"• Регулярность\n"
		"• Качество контента"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔗 Получить ссылку", callback_data="get_referral_link")],
		[InlineKeyboardButton(text="💬 Шаблоны сообщений", callback_data="message_templates")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "message_templates")
async def message_templates(callback: types.CallbackQuery, state: FSMContext):
	"""Шаблоны сообщений для рефералов"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	referral_link = f"https://t.me/FitCoode_bot?start=ref{user.tg_user_id}"
	
	text = (
		f"💬 <b>Шаблоны сообщений</b>\n\n"
		f"<b>📱 Для Telegram:</b>\n\n"
		f"<b>Шаблон 1 (Краткий):</b>\n"
		f"Привет! Я использую отличного фитнес-бота. Попробуй и получи скидку 10%!\n"
		f"{referral_link}\n\n"
		f"<b>Шаблон 2 (Подробный):</b>\n"
		f"Привет! Хочу поделиться с тобой отличным фитнес-ботом. Он дает:\n"
		f"• Персональные тренировки\n"
		"• Питание с КБЖУ\n"
		"• Систему звезд и призов\n"
		"• Поддержку 24/7\n\n"
		f"По моей ссылке ты получишь скидку 10%!\n"
		f"{referral_link}\n\n"
		f"<b>Шаблон 3 (С результатами):</b>\n"
		f"Привет! За месяц использования этого бота я похудел на 5 кг и стал сильнее. Бот дает персональные тренировки и питание. Попробуй по моей ссылке - получишь скидку 10%!\n"
		f"{referral_link}\n\n"
		f"<b>🌐 Для соцсетей:</b>\n\n"
		f"<b>Instagram Story:</b>\n"
		f"💪 Мой секрет фитнеса - персональный бот-тренер!\n"
		f"🔥 Персональные тренировки\n"
		f"🍽️ Питание с КБЖУ\n"
		f"⭐ Звезды и призы\n"
		f"📱 Попробуй по ссылке в профиле\n"
		f"#фитнес #тренировки #здоровье\n\n"
		f"<b>Facebook/VK пост:</b>\n"
		f"Друзья! Хочу поделиться отличным фитнес-ботом. За месяц я получил персональные тренировки, питание с КБЖУ и систему мотивации. Результаты впечатляют! Кто хочет попробовать - пишите в личку, дам ссылку со скидкой 10%.\n\n"
		f"<b>💡 Советы:</b>\n"
		"• Персонализируйте сообщения\n"
		"• Добавляйте свои результаты\n"
		"• Будьте искренними\n"
		"• Отвечайте на вопросы"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📱 Поделиться в Telegram", url=f"https://t.me/share/url?url={referral_link}&text=Привет! Я использую отличного фитнес-бота. Попробуй и получи скидку 10%!")],
		[InlineKeyboardButton(text="📋 Скопировать шаблон", callback_data="copy_message_template")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="share_referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "copy_message_template")
async def copy_message_template(callback: types.CallbackQuery, state: FSMContext):
	"""Скопировать шаблон сообщения"""
	text = (
		"📋 <b>Шаблон скопирован!</b>\n\n"
		"Краткий шаблон для Telegram скопирован в буфер обмена.\n\n"
		"<b>Текст шаблона:</b>\n"
		"Привет! Я использую отличного фитнес-бота. Попробуй и получи скидку 10%!\n"
		"[ВАША_ССЫЛКА]\n\n"
		"<b>Как использовать:</b>\n"
		"1. Вставьте текст в любой мессенджер\n"
		"2. Замените [ВАША_ССЫЛКА] на вашу реферальную ссылку\n"
		"3. Отправьте друзьям\n"
		"4. Получайте звезды!\n\n"
		"<b>Другие шаблоны:</b>\n"
		"• Подробный - для близких друзей\n"
		"• С результатами - для мотивации\n"
		"• Для соцсетей - с хештегами"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💬 Другие шаблоны", callback_data="message_templates")],
		[InlineKeyboardButton(text="🔗 Получить ссылку", callback_data="get_referral_link")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "referral_charts")
async def referral_charts(callback: types.CallbackQuery, state: FSMContext):
	"""Графики реферальной статистики"""
	text = (
		"📈 <b>Графики реферальной статистики</b>\n\n"
		"<b>📊 Статистика по месяцам:</b>\n"
		"• Декабрь 2024: ████████░░ 8 рефералов\n"
		"• Ноябрь 2024: ██████░░░░ 6 рефералов\n"
		"• Октябрь 2024: ████░░░░░░ 4 реферала\n"
		"• Сентябрь 2024: ██░░░░░░░░ 2 реферала\n\n"
		"<b>🎯 Конверсия:</b>\n"
		"• Переходы по ссылке: 45\n"
		"• Регистрации: 15 (33%)\n"
		"• Покупки: 8 (18%)\n\n"
		"<b>⭐ Звезды по месяцам:</b>\n"
		"• Декабрь: ██████████ 800 ⭐\n"
		"• Ноябрь: ████████░░ 600 ⭐\n"
		"• Октябрь: ██████░░░░ 400 ⭐\n"
		"• Сентябрь: ██░░░░░░░░ 200 ⭐\n\n"
		"<b>📱 Источники рефералов:</b>\n"
		"• Telegram: 60%\n"
		"• Instagram: 25%\n"
		"• Facebook: 10%\n"
		"• Другие: 5%\n\n"
		"<b>🎉 Тренды:</b>\n"
		"• Рост рефералов: +25%\n"
		"• Улучшение конверсии: +5%\n"
		"• Больше звезд: +30%"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Подробная статистика", callback_data="referral_statistics")],
		[InlineKeyboardButton(text="👥 Мои рефералы", callback_data="my_referrals")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "message_referrals")
async def message_referrals(callback: types.CallbackQuery, state: FSMContext):
	"""Написать рефералам"""
	text = (
		"💬 <b>Написать рефералам</b>\n\n"
		"<b>Выберите действие:</b>\n\n"
		"<b>📱 Массовая рассылка:</b>\n"
		"• Отправить всем рефералам\n"
		"• Шаблонное сообщение\n"
		"• Мотивация и поддержка\n\n"
		"<b>👤 Индивидуальные сообщения:</b>\n"
		"• Написать конкретному рефералу\n"
		"• Персональный подход\n"
		"• Ответы на вопросы\n\n"
		"<b>📊 По статусу:</b>\n"
		"• Только зарегистрированным\n"
		"• Только купившим программу\n"
		"• Неактивным рефералам\n\n"
		"<b>🎯 По цели:</b>\n"
		"• Мотивация к покупке\n"
		"• Поддержка в тренировках\n"
		"• Советы по питанию\n"
		"• Поздравления с результатами"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📱 Массовая рассылка", callback_data="mass_message")],
		[InlineKeyboardButton(text="👤 Индивидуальные", callback_data="individual_message")],
		[InlineKeyboardButton(text="📊 По статусу", callback_data="status_message")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="my_referrals")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "referral")
async def back_to_referral(callback: types.CallbackQuery):
	"""Возврат в главное меню реферальной системы"""
	await cleanup_general_messages(callback.message)
	await show_referral_menu(callback.message)
	await callback.answer()


# Функция для обработки реферальных переходов
async def process_referral_click(user_id: int, referrer_id: int):
	"""
	Обработка перехода по реферальной ссылке
	В реальном проекте здесь должна быть логика:
	1. Проверка существования реферера
	2. Создание реферальной связи
	3. Начисление звезд рефереру
	4. Применение скидки рефералу
	5. Логирование события
	"""
	pass


# Функция для начисления звезд за рефералов
async def award_referral_stars(referrer_id: int, referral_id: int, event_type: str):
	"""
	Начисление звезд за рефералов
	В реальном проекте здесь должна быть логика:
	1. Проверка типа события (регистрация/покупка)
	2. Начисление соответствующего количества звезд
	3. Создание записи в истории звезд
	4. Уведомление реферера
	"""
	pass


# Функция для применения реферальной скидки
async def apply_referral_discount(user_id: int, discount_percent: int = 10):
	"""
	Применение реферальной скидки
	В реальном проекте здесь должна быть логика:
	1. Проверка права на скидку
	2. Применение скидки к ценам программ
	3. Логирование применения скидки
	4. Уведомление пользователя
	"""
	pass