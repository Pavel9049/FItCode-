from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_support_messages
from app.db.models import ProgramLevel
import json

router = Router()


class SupportStates(StatesGroup):
	choosing_action = State()
	writing_message = State()
	selecting_issue = State()


@router.message(Command("support"))
async def support_command(message: types.Message):
	"""Команда поддержки"""
	await cleanup_general_messages(message)
	await show_support_menu(message)


async def show_support_menu(message: types.Message):
	"""Показать главное меню поддержки"""
	# Проверяем доступ пользователя
	if not await user_has_paid_access(message.from_user.id):
		await message.answer("❌ Для доступа к поддержке необходимо приобрести программу.")
		return
	
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
		return
	
	# Проверяем уровень пользователя для PRO поддержки
	is_pro = user.level and user.level.value in ['advanced', 'pro']
	
	text = (
		f"💬 <b>Поддержка</b>\n\n"
		f"Уровень: {user.level.value.title() if user.level else 'Не выбран'}\n"
		f"Поддержка: {'24/7 PRO' if is_pro else 'Базовая'}\n\n"
		"Выберите тип поддержки:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
		[InlineKeyboardButton(text="📋 Инструкции", callback_data="instructions")],
		[InlineKeyboardButton(text="🐛 Сообщить об ошибке", callback_data="report_bug")],
		[InlineKeyboardButton(text="💡 Предложить идею", callback_data="suggest_idea")],
		[InlineKeyboardButton(text="📞 Связаться с поддержкой", callback_data="contact_support")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_support")
async def cabinet_support_callback(callback: types.CallbackQuery):
	"""Обработка кнопки поддержки из личного кабинета"""
	await cleanup_general_messages(callback.message)
	await show_support_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "faq")
async def faq(callback: types.CallbackQuery, state: FSMContext):
	"""Часто задаваемые вопросы"""
	text = (
		"❓ <b>Часто задаваемые вопросы</b>\n\n"
		"<b>Общие вопросы:</b>\n"
		"• Как начать тренировки?\n"
		"• Как работает система звезд?\n"
		"• Как получить приз?\n"
		"• Как пригласить друга?\n\n"
		"<b>Технические вопросы:</b>\n"
		"• Бот не отвечает\n"
		"• Не работает оплата\n"
		"• Проблемы с видео\n"
		"• Ошибки в меню\n\n"
		"<b>Вопросы по питанию:</b>\n"
		"• Как рассчитать КБЖУ?\n"
		"• Что делать, если нет ингредиентов?\n"
		"• Можно ли заменить блюда?\n\n"
		"Выберите категорию:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📋 Общие вопросы", callback_data="faq_general")],
		[InlineKeyboardButton(text="🔧 Технические вопросы", callback_data="faq_technical")],
		[InlineKeyboardButton(text="🍽️ Вопросы по питанию", callback_data="faq_nutrition")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "faq_general")
async def faq_general(callback: types.CallbackQuery, state: FSMContext):
	"""Общие вопросы FAQ"""
	text = (
		"📋 <b>Общие вопросы</b>\n\n"
		"<b>Q: Как начать тренировки?</b>\n"
		"A: Выберите программу в /start, оплатите доступ, затем перейдите в раздел 'Тренировки'.\n\n"
		"<b>Q: Как работает система звезд?</b>\n"
		"A: Звезды начисляются за тренировки, загрузку фото прогресса, достижение целей и приглашение друзей.\n\n"
		"<b>Q: Как получить приз?</b>\n"
		"A: Накопите звезды и обменяйте их на призы в разделе 'Звезды и призы'.\n\n"
		"<b>Q: Как пригласить друга?</b>\n"
		"A: Получите реферальную ссылку в разделе 'Звезды и призы' и поделитесь с другом.\n\n"
		"<b>Q: Что такое ежемесячный розыгрыш?</b>\n"
		"A: 1-го числа месяца топ-5 пользователей по звездам получают призы."
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔧 Технические вопросы", callback_data="faq_technical")],
		[InlineKeyboardButton(text="🍽️ Вопросы по питанию", callback_data="faq_nutrition")],
		[InlineKeyboardButton(text="🔙 Назад к FAQ", callback_data="faq")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "faq_technical")
async def faq_technical(callback: types.CallbackQuery, state: FSMContext):
	"""Технические вопросы FAQ"""
	text = (
		"🔧 <b>Технические вопросы</b>\n\n"
		"<b>Q: Бот не отвечает</b>\n"
		"A: Попробуйте перезапустить бота командой /start или обратитесь в поддержку.\n\n"
		"<b>Q: Не работает оплата</b>\n"
		"A: Проверьте баланс карты, попробуйте другой способ оплаты или обратитесь в поддержку.\n\n"
		"<b>Q: Проблемы с видео</b>\n"
		"A: Видео могут загружаться медленно. Попробуйте позже или используйте стабильное интернет-соединение.\n\n"
		"<b>Q: Ошибки в меню</b>\n"
		"A: Очистите чат с ботом и начните заново с /start.\n\n"
		"<b>Q: Не сохраняются настройки</b>\n"
		"A: Проверьте подключение к интернету и попробуйте еще раз."
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📋 Общие вопросы", callback_data="faq_general")],
		[InlineKeyboardButton(text="🍽️ Вопросы по питанию", callback_data="faq_nutrition")],
		[InlineKeyboardButton(text="🔙 Назад к FAQ", callback_data="faq")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "faq_nutrition")
async def faq_nutrition(callback: types.CallbackQuery, state: FSMContext):
	"""Вопросы по питанию FAQ"""
	text = (
		"🍽️ <b>Вопросы по питанию</b>\n\n"
		"<b>Q: Как рассчитать КБЖУ?</b>\n"
		"A: Бот автоматически рассчитывает КБЖУ на основе вашего веса, роста, возраста и целей.\n\n"
		"<b>Q: Что делать, если нет ингредиентов?</b>\n"
		"A: Используйте поиск блюд для замены или обратитесь к персональному питанию.\n\n"
		"<b>Q: Можно ли заменить блюда?</b>\n"
		"A: Да, используйте поиск блюд или персональное питание для подбора альтернатив.\n\n"
		"<b>Q: Как работает AI анализ фото?</b>\n"
		"A: Отправьте фото блюда, и бот определит примерные КБЖУ (приблизительная оценка).\n\n"
		"<b>Q: Меню обновляется?</b>\n"
		"A: Да, меню обновляется еженедельно с новыми блюдами."
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📋 Общие вопросы", callback_data="faq_general")],
		[InlineKeyboardButton(text="🔧 Технические вопросы", callback_data="faq_technical")],
		[InlineKeyboardButton(text="🔙 Назад к FAQ", callback_data="faq")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "instructions")
async def instructions(callback: types.CallbackQuery, state: FSMContext):
	"""Инструкции"""
	text = (
		"📋 <b>Инструкции</b>\n\n"
		"<b>Быстрый старт:</b>\n"
		"1. Выберите программу в /start\n"
		"2. Оплатите доступ\n"
		"3. Настройте профиль в настройках\n"
		"4. Начните первую тренировку\n\n"
		"<b>Как тренироваться:</b>\n"
		"1. Перейдите в раздел 'Тренировки'\n"
		"2. Выберите тип тренировки\n"
		"3. Следуйте инструкциям\n"
		"4. Отмечайте выполненные упражнения\n\n"
		"<b>Как питаться:</b>\n"
		"1. Перейдите в раздел 'Меню'\n"
		"2. Выберите день недели\n"
		"3. Следуйте рецептам\n"
		"4. Используйте AI анализ фото\n\n"
		"<b>Как заработать звезды:</b>\n"
		"• Тренируйтесь регулярно\n"
		"• Загружайте фото прогресса\n"
		"• Достигайте целей\n"
		"• Приглашайте друзей"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🎯 Подробные инструкции", callback_data="detailed_instructions")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "detailed_instructions")
async def detailed_instructions(callback: types.CallbackQuery, state: FSMContext):
	"""Подробные инструкции"""
	text = (
		"🎯 <b>Подробные инструкции</b>\n\n"
		"<b>Настройка профиля:</b>\n"
		"1. Перейдите в настройки\n"
		"2. Укажите вес, рост, возраст, пол\n"
		"3. Установите цели\n"
		"4. Настройте уведомления\n\n"
		"<b>Тренировки:</b>\n"
		"• Bodyweight: тренировки без инвентаря\n"
		"• Split: сплит-тренировки по группам мышц\n"
		"• Personal: персональный план\n"
		"• Muscle groups: упражнения по группам мышц\n\n"
		"<b>Питание:</b>\n"
		"• Weekly menu: меню на неделю\n"
		"• Personal nutrition: персональное питание\n"
		"• Search meals: поиск блюд\n"
		"• AI photo analysis: анализ фото\n\n"
		"<b>Звезды и призы:</b>\n"
		"• Загружайте фото прогресса\n"
		"• Обменивайте звезды на призы\n"
		"• Участвуйте в розыгрышах\n"
		"• Приглашайте друзей"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад к инструкциям", callback_data="instructions")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "report_bug")
async def report_bug(callback: types.CallbackQuery, state: FSMContext):
	"""Сообщить об ошибке"""
	text = (
		"🐛 <b>Сообщить об ошибке</b>\n\n"
		"Опишите проблему, которую вы обнаружили:\n\n"
		"<b>Что включить в сообщение:</b>\n"
		"• Что вы делали, когда возникла ошибка\n"
		"• Какое сообщение об ошибке вы видели\n"
		"• На каком устройстве вы используете бота\n"
		"• Версия Telegram\n\n"
		"<b>Пример:</b>\n"
		"\"При попытке открыть тренировки бот выдает ошибку 'Не удалось загрузить упражнения'. Использую iPhone, Telegram версия 9.0\"\n\n"
		"Введите описание ошибки:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SupportStates.writing_message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "suggest_idea")
async def suggest_idea(callback: types.CallbackQuery, state: FSMContext):
	"""Предложить идею"""
	text = (
		"💡 <b>Предложить идею</b>\n\n"
		"Расскажите о вашей идее для улучшения бота:\n\n"
		"<b>Что включить в предложение:</b>\n"
		"• Описание новой функции\n"
		"• Как это поможет пользователям\n"
		"• Примеры использования\n"
		"• Приоритет (важно/средне/не важно)\n\n"
		"<b>Пример:</b>\n"
		"\"Предлагаю добавить функцию экспорта тренировок в календарь. Это поможет планировать тренировки заранее. Приоритет: средний\"\n\n"
		"Введите ваше предложение:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SupportStates.writing_message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "contact_support")
async def contact_support(callback: types.CallbackQuery, state: FSMContext):
	"""Связаться с поддержкой"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	# Проверяем уровень пользователя для PRO поддержки
	is_pro = user.level and user.level.value in ['advanced', 'pro']
	
	if is_pro:
		text = (
			f"📞 <b>24/7 PRO Поддержка</b>\n\n"
			f"Уровень: {user.level.value.title()}\n"
			f"Статус: PRO поддержка\n\n"
			f"<b>Доступные каналы:</b>\n"
			"• Прямой чат с тренером\n"
			"• Приоритетная поддержка\n"
			"• Персональные консультации\n"
			"• Быстрые ответы\n\n"
			f"<b>Время работы:</b> 24/7\n\n"
			"Выберите способ связи:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="💬 Чат с тренером", callback_data="chat_with_trainer")],
			[InlineKeyboardButton(text="📧 Написать сообщение", callback_data="write_to_support")],
			[InlineKeyboardButton(text="📞 Экстренная связь", callback_data="emergency_contact")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="support")]
		])
	else:
		text = (
			f"📞 <b>Базовая поддержка</b>\n\n"
			f"Уровень: {user.level.value.title() if user.level else 'Не выбран'}\n"
			"Статус: Базовая поддержка\n\n"
			f"<b>Доступные каналы:</b>\n"
			"• FAQ и инструкции\n"
			"• Сообщения об ошибках\n"
			"• Предложения идей\n"
			"• Email поддержка\n\n"
			f"<b>Время работы:</b> Пн-Пт, 9:00-18:00\n\n"
			f"<b>Для 24/7 поддержки:</b>\n"
			"Обновите программу до уровня 'Продвинутый' или 'Профессионал'.\n\n"
			"Выберите способ связи:"
		)
		
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="📧 Написать сообщение", callback_data="write_to_support")],
			[InlineKeyboardButton(text="💎 Обновить программу", callback_data="upgrade_for_support")],
			[InlineKeyboardButton(text="🔙 Назад", callback_data="support")]
		])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "write_to_support")
async def write_to_support(callback: types.CallbackQuery, state: FSMContext):
	"""Написать в поддержку"""
	text = (
		"📧 <b>Написать в поддержку</b>\n\n"
		"Опишите ваш вопрос или проблему:\n\n"
		"<b>Рекомендации:</b>\n"
		"• Будьте конкретны\n"
		"• Укажите ваш уровень программы\n"
		"• Приложите скриншоты, если нужно\n"
		"• Опишите шаги для воспроизведения\n\n"
		"<b>Время ответа:</b>\n"
		"• Базовая поддержка: до 24 часов\n"
		"• PRO поддержка: до 2 часов\n\n"
		"Введите ваше сообщение:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="contact_support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SupportStates.writing_message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "chat_with_trainer")
async def chat_with_trainer(callback: types.CallbackQuery, state: FSMContext):
	"""Чат с тренером"""
	text = (
		"💬 <b>Чат с тренером</b>\n\n"
		"<b>Ваш тренер:</b> Алексей Петров\n"
		"<b>Опыт:</b> 8 лет в фитнесе\n"
		"<b>Специализация:</b> Силовые тренировки, питание\n\n"
		"<b>Что можно обсудить:</b>\n"
		"• Технику выполнения упражнений\n"
		"• Персональные планы тренировок\n"
		"• Вопросы по питанию\n"
		"• Мотивацию и цели\n"
		"• Прогресс и результаты\n\n"
		"<b>Время работы:</b> 24/7\n"
		"<b>Время ответа:</b> до 30 минут\n\n"
		"Напишите ваш вопрос тренеру:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="contact_support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SupportStates.writing_message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "emergency_contact")
async def emergency_contact(callback: types.CallbackQuery, state: FSMContext):
	"""Экстренная связь"""
	text = (
		"🚨 <b>Экстренная связь</b>\n\n"
		"<b>Используйте только в критических случаях:</b>\n"
		"• Проблемы с оплатой\n"
		"• Технические сбои\n"
		"• Безопасность аккаунта\n"
		"• Срочные вопросы\n\n"
		"<b>Время ответа:</b> до 15 минут\n"
		"<b>Доступно:</b> 24/7\n\n"
		"<b>Контакты:</b>\n"
		"• Telegram: @FitCoachSupport\n"
		"• Email: emergency@fitcoach.bot\n"
		"• Телефон: +7 (999) 123-45-67\n\n"
		"Опишите вашу экстренную ситуацию:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="contact_support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(SupportStates.writing_message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "upgrade_for_support")
async def upgrade_for_support(callback: types.CallbackQuery, state: FSMContext):
	"""Обновить программу для поддержки"""
	text = (
		"💎 <b>Обновить программу</b>\n\n"
		"<b>PRO поддержка включает:</b>\n"
		"• 24/7 чат с тренером\n"
		"• Приоритетная поддержка\n"
		"• Персональные консультации\n"
		"• Быстрые ответы (до 2 часов)\n"
		"• Экстренная связь\n\n"
		"<b>Доступные программы:</b>\n"
		"• Продвинутый - 2990 ₽/месяц\n"
		"• Профессионал - 4990 ₽/месяц\n\n"
		"<b>Дополнительные преимущества:</b>\n"
		"• Персональное питание\n"
		"• Расширенная база упражнений\n"
		"• Приоритетные обновления\n"
		"• Эксклюзивный контент"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💎 Обновить программу", callback_data="upgrade_program")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="contact_support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.message(SupportStates.writing_message)
async def process_support_message(message: types.Message, state: FSMContext):
	"""Обработка сообщения в поддержку"""
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
		await state.clear()
		return
	
	# В реальном проекте здесь должна быть логика сохранения сообщения в БД
	# и отправки уведомления администраторам
	
	text = (
		f"✅ <b>Сообщение отправлено!</b>\n\n"
		f"<b>Ваше сообщение:</b>\n"
		f"{message.text[:200]}{'...' if len(message.text) > 200 else ''}\n\n"
		f"<b>Статус:</b> Обрабатывается\n"
		f"<b>Время ответа:</b> {'до 2 часов' if user.level and user.level.value in ['advanced', 'pro'] else 'до 24 часов'}\n\n"
		"Мы свяжемся с вами в ближайшее время.\n\n"
		f"<b>Номер обращения:</b> #{user.id}_{int(message.date.timestamp())}"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📧 Отправить еще сообщение", callback_data="write_to_support")],
		[InlineKeyboardButton(text="🔙 Назад в поддержку", callback_data="support")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")
	await state.clear()


@router.callback_query(lambda c: c.data == "support")
async def back_to_support(callback: types.CallbackQuery):
	"""Возврат в главное меню поддержки"""
	await cleanup_general_messages(callback.message)
	await show_support_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "upgrade_program")
async def upgrade_program(callback: types.CallbackQuery, state: FSMContext):
	"""Обновить программу"""
	text = (
		"💎 <b>Обновить программу</b>\n\n"
		"Выберите новую программу:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🚀 Продвинутый - 2990 ₽/мес", callback_data="upgrade_to_advanced")],
		[InlineKeyboardButton(text="👑 Профессионал - 4990 ₽/мес", callback_data="upgrade_to_pro")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="upgrade_for_support")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("upgrade_to_"))
async def process_upgrade(callback: types.CallbackQuery, state: FSMContext):
	"""Обработка обновления программы"""
	program = callback.data.split("_")[-1]
	
	program_names = {
		'advanced': 'Продвинутый',
		'pro': 'Профессионал'
	}
	
	program_prices = {
		'advanced': '2990',
		'pro': '4990'
	}
	
	text = (
		f"💎 <b>Обновление до {program_names[program]}</b>\n\n"
		f"<b>Стоимость:</b> {program_prices[program]} ₽/месяц\n\n"
		f"<b>Включено:</b>\n"
		f"• 24/7 PRO поддержка\n"
		"• Персональное питание\n"
		"• Расширенная база упражнений\n"
		"• Приоритетные обновления\n"
		"• Эксклюзивный контент\n\n"
		"Перейти к оплате?"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_upgrade:{program}")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="upgrade_program")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()