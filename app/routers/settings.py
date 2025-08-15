from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access, update_user_profile, toggle_user_notifications
from app.utils.chat_cleanup import cleanup_settings_messages
from app.db.models import ProgramLevel
import json

router = Router()


class SettingsStates(StatesGroup):
	choosing_action = State()
	editing_profile = State()
	editing_goals = State()
	setting_weight = State()
	setting_height = State()
	setting_age = State()
	setting_gender = State()


@router.message(Command("settings"))
async def settings_command(message: types.Message):
	"""Команда настроек"""
	await show_settings_menu(message)


async def show_settings_menu(message: types.Message):
	"""Показать главное меню настроек"""
	# Проверяем доступ пользователя
	if not await user_has_paid_access(message.from_user.id):
		await message.answer("❌ Для доступа к настройкам необходимо приобрести программу.")
		return
	
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
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
		[InlineKeyboardButton(text="📊 Статистика", callback_data="view_stats")],
		[InlineKeyboardButton(text="🔒 Приватность", callback_data="privacy_settings")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_settings")
async def cabinet_settings_callback(callback: types.CallbackQuery):
	"""Обработка кнопки настроек из личного кабинета"""
	await show_settings_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "toggle_notifications")
async def toggle_notifications(callback: types.CallbackQuery, state: FSMContext):
	"""Переключить уведомления"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Переключаем уведомления
	new_status = await toggle_user_notifications(callback.from_user.id)
	status_text = "✅ Включены" if new_status else "❌ Отключены"
	
	text = (
		f"🔔 <b>Уведомления</b>\n\n"
		f"Статус: {status_text}\n\n"
		"<b>Типы уведомлений:</b>\n"
		"• Мотивационные сообщения\n"
		"• Напоминания о тренировках\n"
		"• Советы по питанию\n"
		"• Анонсы новых блюд\n"
		"• Напоминания о звездах\n"
		"• Еженедельные проверки прогресса\n"
		"• Напоминания о целях\n"
		"• Реферальные напоминания\n"
		"• Ежемесячные розыгрыши"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔄 Переключить", callback_data="toggle_notifications")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery, state: FSMContext):
	"""Редактировать профиль"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"👤 <b>Редактирование профиля</b>\n\n"
		f"<b>Текущие данные:</b>\n"
		f"• Имя: {user.first_name or 'Не указано'}\n"
		f"• Вес: {user.weight_kg or 'Не указан'} кг\n"
		f"• Рост: {user.height_cm or 'Не указан'} см\n"
		f"• Возраст: {user.age or 'Не указан'} лет\n"
		f"• Пол: {user.gender or 'Не указан'}\n\n"
		"Выберите, что хотите изменить:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="⚖️ Вес", callback_data="set_weight")],
		[InlineKeyboardButton(text="📏 Рост", callback_data="set_height")],
		[InlineKeyboardButton(text="🎂 Возраст", callback_data="set_age")],
		[InlineKeyboardButton(text="👥 Пол", callback_data="set_gender")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "set_weight")
async def set_weight(callback: types.CallbackQuery, state: FSMContext):
	"""Установить вес"""
	text = (
		"⚖️ <b>Установить вес</b>\n\n"
		"Введите ваш текущий вес в килограммах.\n"
		"Например: 75.5"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SettingsStates.setting_weight)
	await callback.answer()


@router.message(SettingsStates.setting_weight)
async def process_weight_setting(message: types.Message, state: FSMContext):
	"""Обработка установки веса"""
	try:
		weight = float(message.text.replace(',', '.'))
		if weight < 30 or weight > 300:
			await message.answer("❌ Вес должен быть от 30 до 300 кг. Попробуйте еще раз.")
			return
		
		# Обновляем вес в базе данных
		success = await update_user_profile(message.from_user.id, weight_kg=weight)
		
		if success:
			text = f"✅ <b>Вес обновлен!</b>\n\nНовый вес: {weight} кг"
		else:
			text = "❌ Ошибка при обновлении веса. Попробуйте еще раз."
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="👤 Продолжить редактирование", callback_data="edit_profile")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
		])
		
		await message.answer(text, reply_markup=kb, parse_mode="HTML")
		await state.clear()
		
	except ValueError:
		await message.answer("❌ Неверный формат веса. Введите число, например: 75.5")


@router.callback_query(lambda c: c.data == "set_height")
async def set_height(callback: types.CallbackQuery, state: FSMContext):
	"""Установить рост"""
	text = (
		"📏 <b>Установить рост</b>\n\n"
		"Введите ваш рост в сантиметрах.\n"
		"Например: 175"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SettingsStates.setting_height)
	await callback.answer()


@router.message(SettingsStates.setting_height)
async def process_height_setting(message: types.Message, state: FSMContext):
	"""Обработка установки роста"""
	try:
		height = int(message.text)
		if height < 100 or height > 250:
			await message.answer("❌ Рост должен быть от 100 до 250 см. Попробуйте еще раз.")
			return
		
		# Обновляем рост в базе данных
		success = await update_user_profile(message.from_user.id, height_cm=height)
		
		if success:
			text = f"✅ <b>Рост обновлен!</b>\n\nНовый рост: {height} см"
		else:
			text = "❌ Ошибка при обновлении роста. Попробуйте еще раз."
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="👤 Продолжить редактирование", callback_data="edit_profile")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
		])
		
		await message.answer(text, reply_markup=kb, parse_mode="HTML")
		await state.clear()
		
	except ValueError:
		await message.answer("❌ Неверный формат роста. Введите целое число, например: 175")


@router.callback_query(lambda c: c.data == "set_age")
async def set_age(callback: types.CallbackQuery, state: FSMContext):
	"""Установить возраст"""
	text = (
		"🎂 <b>Установить возраст</b>\n\n"
		"Введите ваш возраст в годах.\n"
		"Например: 25"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SettingsStates.setting_age)
	await callback.answer()


@router.message(SettingsStates.setting_age)
async def process_age_setting(message: types.Message, state: FSMContext):
	"""Обработка установки возраста"""
	try:
		age = int(message.text)
		if age < 14 or age > 100:
			await message.answer("❌ Возраст должен быть от 14 до 100 лет. Попробуйте еще раз.")
			return
		
		# Обновляем возраст в базе данных
		success = await update_user_profile(message.from_user.id, age=age)
		
		if success:
			text = f"✅ <b>Возраст обновлен!</b>\n\nНовый возраст: {age} лет"
		else:
			text = "❌ Ошибка при обновлении возраста. Попробуйте еще раз."
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="👤 Продолжить редактирование", callback_data="edit_profile")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
		])
		
		await message.answer(text, reply_markup=kb, parse_mode="HTML")
		await state.clear()
		
	except ValueError:
		await message.answer("❌ Неверный формат возраста. Введите целое число, например: 25")


@router.callback_query(lambda c: c.data == "set_gender")
async def set_gender(callback: types.CallbackQuery, state: FSMContext):
	"""Установить пол"""
	text = (
		"👥 <b>Установить пол</b>\n\n"
		"Выберите ваш пол:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="👨 Мужской", callback_data="set_gender_male")],
		[InlineKeyboardButton(text="👩 Женский", callback_data="set_gender_female")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("set_gender_"))
async def process_gender_setting(callback: types.CallbackQuery, state: FSMContext):
	"""Обработка установки пола"""
	gender = callback.data.split("_")[-1]
	gender_text = "Мужской" if gender == "male" else "Женский"
	
	# Обновляем пол в базе данных
	success = await update_user_profile(callback.from_user.id, gender=gender)
	
	if success:
		text = f"✅ <b>Пол обновлен!</b>\n\nНовый пол: {gender_text}"
	else:
		text = "❌ Ошибка при обновлении пола. Попробуйте еще раз."
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="👤 Продолжить редактирование", callback_data="edit_profile")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "edit_goals")
async def edit_goals(callback: types.CallbackQuery, state: FSMContext):
	"""Редактировать цели"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"🎯 <b>Редактирование целей</b>\n\n"
		f"<b>Текущие цели:</b>\n"
		f"• Основная цель: Не установлена\n"
		"• Целевой вес: Не установлен\n"
		"• Срок достижения: Не установлен\n\n"
		"Выберите действие:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🎯 Установить новую цель", callback_data="set_new_goal")],
		[InlineKeyboardButton(text="📊 Просмотреть цели", callback_data="view_goals")],
		[InlineKeyboardButton(text="📈 Прогресс к целям", callback_data="goal_progress")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "set_new_goal")
async def set_new_goal(callback: types.CallbackQuery, state: FSMContext):
	"""Установить новую цель"""
	text = (
		"🎯 <b>Установить новую цель</b>\n\n"
		"Выберите основную цель:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💪 Набрать массу", callback_data="goal_type:gain_mass")],
		[InlineKeyboardButton(text="🔥 Похудеть", callback_data="goal_type:lose_weight")],
		[InlineKeyboardButton(text="✂️ Подсушиться", callback_data="goal_type:cut")],
		[InlineKeyboardButton(text="🏃 Держать тонус", callback_data="goal_type:tone")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_goals")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("goal_type:"))
async def process_goal_type(callback: types.CallbackQuery, state: FSMContext):
	"""Обработка выбора типа цели"""
	goal_type = callback.data.split(":")[1]
	
	goal_names = {
		'gain_mass': 'Набор массы',
		'lose_weight': 'Похудение',
		'cut': 'Подсушивание',
		'tone': 'Поддержание тонуса'
	}
	
	text = (
		f"🎯 <b>Цель: {goal_names[goal_type]}</b>\n\n"
		f"Теперь установите целевой вес.\n"
		f"Введите желаемый вес в килограммах:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="set_new_goal")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.update_data(goal_type=goal_type)
	await state.set_state(SettingsStates.setting_weight)
	await callback.answer()


@router.callback_query(lambda c: c.data == "view_goals")
async def view_goals(callback: types.CallbackQuery, state: FSMContext):
	"""Просмотреть цели"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# В реальном проекте здесь должна быть логика получения целей из БД
	# Пока что показываем заглушку
	
	text = (
		f"📊 <b>Ваши цели</b>\n\n"
		f"<b>Активные цели:</b>\n"
		"• Похудеть на 5 кг за 3 месяца\n"
		"• Увеличить мышечную массу\n"
		"• Улучшить выносливость\n\n"
		"<b>Завершенные цели:</b>\n"
		"• Начать регулярные тренировки ✅\n"
		"• Изучить базовые упражнения ✅\n\n"
		"<b>Прогресс:</b>\n"
		"• Общий прогресс: 65%\n"
		"• Время до цели: 2 месяца"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🎯 Установить новую цель", callback_data="set_new_goal")],
		[InlineKeyboardButton(text="📈 Детальный прогресс", callback_data="goal_progress")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_goals")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "goal_progress")
async def goal_progress(callback: types.CallbackQuery, state: FSMContext):
	"""Прогресс к целям"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"📈 <b>Прогресс к целям</b>\n\n"
		f"<b>Цель: Похудеть на 5 кг</b>\n"
		f"• Начальный вес: 80 кг\n"
		f"• Текущий вес: 77 кг\n"
		f"• Целевой вес: 75 кг\n"
		f"• Прогресс: 60%\n"
		f"• Осталось: 2 кг\n\n"
		f"<b>Цель: Увеличить мышечную массу</b>\n"
		"• Прогресс: 40%\n"
		"• Тренировок выполнено: 12/30\n\n"
		f"<b>Цель: Улучшить выносливость</b>\n"
		"• Прогресс: 75%\n"
		"• Кардио сессий: 8/10"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Подробная статистика", callback_data="detailed_goal_stats")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="edit_goals")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "view_stats")
async def view_stats(callback: types.CallbackQuery, state: FSMContext):
	"""Просмотреть статистику"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"📊 <b>Ваша статистика</b>\n\n"
		f"<b>Общая информация:</b>\n"
		f"• Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}\n"
		f"• Уровень: {user.level.value.title() if user.level else 'Не выбран'}\n"
		f"• Звезды: {user.stars} ⭐\n\n"
		f"<b>Тренировки:</b>\n"
		"• Всего тренировок: 25\n"
		"• Тренировок в неделю: 4\n"
		"• Любимое упражнение: Приседания\n\n"
		f"<b>Питание:</b>\n"
		"• Приемов пищи: 156\n"
		"• Средние калории: 2100\n"
		"• Соблюдение плана: 85%\n\n"
		f"<b>Прогресс:</b>\n"
		"• Изменение веса: -3 кг\n"
		"• Фото прогресса: 5\n"
		"• Целей достигнуто: 2"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📈 Детальная статистика", callback_data="detailed_stats")],
		[InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "privacy_settings")
async def privacy_settings(callback: types.CallbackQuery, state: FSMContext):
	"""Настройки приватности"""
	text = (
		"🔒 <b>Настройки приватности</b>\n\n"
		"<b>Текущие настройки:</b>\n"
		"• Показывать прогресс в топах: ✅\n"
		"• Разрешить сообщения от других пользователей: ❌\n"
		"• Показывать статистику в профиле: ✅\n"
		"• Разрешить уведомления: ✅\n\n"
		"Выберите настройку для изменения:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Показывать в топах", callback_data="toggle_show_in_tops")],
		[InlineKeyboardButton(text="💬 Сообщения от пользователей", callback_data="toggle_user_messages")],
		[InlineKeyboardButton(text="👤 Статистика в профиле", callback_data="toggle_profile_stats")],
		[InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")],
		[InlineKeyboardButton(text="🗑️ Удалить аккаунт", callback_data="delete_account")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "toggle_show_in_tops")
async def toggle_show_in_tops(callback: types.CallbackQuery, state: FSMContext):
	"""Переключить показ в топах"""
	text = (
		"📊 <b>Показ в топах</b>\n\n"
		"<b>Текущий статус:</b> ✅ Включено\n\n"
		"<b>Что это означает:</b>\n"
		"• Ваш прогресс может отображаться в топах\n"
		"• Другие пользователи могут видеть ваши достижения\n"
		"• Это помогает мотивировать других\n\n"
		"<b>Конфиденциальность:</b>\n"
		"• Показывается только никнейм и прогресс\n"
		"• Личные данные не раскрываются\n"
		"• Можно отключить в любой момент"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="❌ Отключить", callback_data="disable_show_in_tops")],
		[InlineKeyboardButton(text="✅ Оставить включенным", callback_data="keep_show_in_tops")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="privacy_settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "delete_account")
async def delete_account(callback: types.CallbackQuery, state: FSMContext):
	"""Удалить аккаунт"""
	text = (
		"🗑️ <b>Удаление аккаунта</b>\n\n"
		"<b>⚠️ Внимание!</b>\n"
		"Удаление аккаунта необратимо.\n\n"
		"<b>Что будет удалено:</b>\n"
		"• Все данные профиля\n"
		"• История тренировок\n"
		"• Фото прогресса\n"
		"• Звезды и призы\n"
		"• Настройки\n\n"
		"<b>Что НЕ будет удалено:</b>\n"
		"• История платежей (для налоговых целей)\n\n"
		"<b>Альтернативы:</b>\n"
		"• Временно отключить уведомления\n"
		"• Скрыть профиль от других пользователей\n"
		"• Обратиться в поддержку\n\n"
		"Вы уверены, что хотите удалить аккаунт?"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🗑️ Да, удалить аккаунт", callback_data="confirm_delete_account")],
		[InlineKeyboardButton(text="❌ Отмена", callback_data="privacy_settings")],
		[InlineKeyboardButton(text="💬 Обратиться в поддержку", callback_data="contact_support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "confirm_delete_account")
async def confirm_delete_account(callback: types.CallbackQuery, state: FSMContext):
	"""Подтверждение удаления аккаунта"""
	text = (
		"🗑️ <b>Подтверждение удаления</b>\n\n"
		"Для подтверждения удаления аккаунта введите:\n\n"
		"<code>УДАЛИТЬ АККАУНТ</code>\n\n"
		"<b>⚠️ Это действие необратимо!</b>"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="❌ Отмена", callback_data="privacy_settings")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SettingsStates.choosing_action)
	await callback.answer()


@router.callback_query(lambda c: c.data == "settings")
async def back_to_settings(callback: types.CallbackQuery):
	"""Возврат в главное меню настроек"""
	await show_settings_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "detailed_stats")
async def detailed_stats(callback: types.CallbackQuery, state: FSMContext):
	"""Детальная статистика"""
	text = (
		"📈 <b>Детальная статистика</b>\n\n"
		"<b>Тренировки:</b>\n"
		"• Всего тренировок: 25\n"
		"• Тренировок в неделю: 4\n"
		"• Средняя продолжительность: 45 мин\n"
		"• Любимое упражнение: Приседания\n"
		"• Самая длинная серия: 7 дней\n\n"
		"<b>Питание:</b>\n"
		"• Приемов пищи: 156\n"
		"• Средние калории: 2100\n"
		"• Средний белок: 120г\n"
		"• Соблюдение плана: 85%\n"
		"• Любимое блюдо: Куриная грудка\n\n"
		"<b>Прогресс:</b>\n"
		"• Изменение веса: -3 кг\n"
		"• Изменение веса в %: -3.6%\n"
		"• Фото прогресса: 5\n"
		"• Целей достигнуто: 2\n"
		"• Звезд заработано: 150"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="view_stats")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "export_data")
async def export_data(callback: types.CallbackQuery, state: FSMContext):
	"""Экспорт данных"""
	text = (
		"📊 <b>Экспорт данных</b>\n\n"
		"Выберите формат для экспорта ваших данных:\n\n"
		"<b>Доступные форматы:</b>\n"
		"• JSON - для технических целей\n"
		"• CSV - для анализа в Excel\n"
		"• PDF - для печати\n\n"
		"<b>Что будет экспортировано:</b>\n"
		"• Данные профиля\n"
		"• История тренировок\n"
		"• Статистика питания\n"
		"• Прогресс и цели\n"
		"• История звезд"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📄 JSON", callback_data="export_json")],
		[InlineKeyboardButton(text="📊 CSV", callback_data="export_csv")],
		[InlineKeyboardButton(text="📋 PDF", callback_data="export_pdf")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="view_stats")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("export_"))
async def process_export(callback: types.CallbackQuery, state: FSMContext):
	"""Обработка экспорта данных"""
	export_format = callback.data.split("_")[1]
	
	text = (
		f"📊 <b>Экспорт данных в {export_format.upper()}</b>\n\n"
		f"Функция находится в разработке.\n"
		"Скоро вы сможете экспортировать свои данные в формате {export_format.upper()}.\n\n"
		f"<b>Что будет доступно:</b>\n"
		"• Полная история тренировок\n"
		"• Статистика питания\n"
		"• Прогресс и достижения\n"
		"• Настройки профиля"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 Другие форматы", callback_data="export_data")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="view_stats")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()