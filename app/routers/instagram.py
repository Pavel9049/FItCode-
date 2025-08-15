from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_instagram_messages
from app.db.models import ProgramLevel
import json
import requests
from datetime import datetime, timedelta

router = Router()


class InstagramStates(StatesGroup):
	choosing_action = State()
	viewing_posts = State()
	participating_challenge = State()


@router.message(Command("instagram"))
async def instagram_command(message: types.Message):
	"""Команда Instagram"""
	await show_instagram_menu(message)


async def show_instagram_menu(message: types.Message):
	"""Показать главное меню Instagram"""
	# Проверяем доступ пользователя
	if not await user_has_paid_access(message.from_user.id):
		await message.answer("❌ Для доступа к Instagram интеграции необходимо приобрести программу.")
		return
	
	text = (
		"📸 <b>Instagram интеграция</b>\n\n"
		"<b>Что доступно:</b>\n"
		"• Последние посты из Instagram\n"
		"• Участие в челленджах\n"
		"• Мотивационные посты\n"
		"• Рецепты и тренировки\n"
		"• Прямая ссылка на профиль\n\n"
		"Выберите действие:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📱 Последние посты", callback_data="instagram_posts")],
		[InlineKeyboardButton(text="🏆 Челенджи", callback_data="instagram_challenges")],
		[InlineKeyboardButton(text="💪 Мотивация", callback_data="instagram_motivation")],
		[InlineKeyboardButton(text="🍽️ Рецепты", callback_data="instagram_recipes")],
		[InlineKeyboardButton(text="🏋️ Тренировки", callback_data="instagram_workouts")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_instagram")
async def cabinet_instagram_callback(callback: types.CallbackQuery):
	"""Обработка кнопки Instagram из личного кабинета"""
	await show_instagram_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "instagram_posts")
async def instagram_posts(callback: types.CallbackQuery, state: FSMContext):
	"""Последние посты из Instagram"""
	# В реальном проекте здесь должна быть логика получения постов через Instagram API
	# Пока что показываем заглушку
	
	text = (
		"📱 <b>Последние посты из Instagram</b>\n\n"
		"<b>Последние публикации:</b>\n\n"
		"<b>1. 💪 Новая тренировка для ног</b>\n"
		"📅 2 часа назад\n"
		"❤️ 1,234 лайка\n"
		"💬 89 комментариев\n\n"
		"<b>2. 🍽️ ПП рецепт: Куриная грудка с овощами</b>\n"
		"📅 5 часов назад\n"
		"❤️ 2,156 лайка\n"
		"💬 156 комментариев\n\n"
		"<b>3. 🏆 Результаты челленджа #30днейприседаний</b>\n"
		"📅 1 день назад\n"
		"❤️ 3,421 лайк\n"
		"💬 234 комментария\n\n"
		"<b>4. 💡 Советы по питанию</b>\n"
		"📅 2 дня назад\n"
		"❤️ 1,890 лайка\n"
		"💬 67 комментариев\n\n"
		"<b>5. 🎯 Мотивация на неделю</b>\n"
		"📅 3 дня назад\n"
		"❤️ 4,567 лайка\n"
		"💬 189 комментариев"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔄 Обновить", callback_data="instagram_posts")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "instagram_challenges")
async def instagram_challenges(callback: types.CallbackQuery, state: FSMContext):
	"""Instagram челленджи"""
	text = (
		"🏆 <b>Instagram челленджи</b>\n\n"
		"<b>Активные челленджи:</b>\n\n"
		"<b>1. #30днейприседаний</b>\n"
		"📅 До 31 декабря\n"
		"👥 1,234 участника\n"
		"🏆 Приз: Беспроводные наушники\n"
		"📝 Описание: 30 дней приседаний с увеличением количества\n\n"
		"<b>2. #ппрецептынедели</b>\n"
		"📅 До 25 декабря\n"
		"👥 567 участников\n"
		"🏆 Приз: Набор специй\n"
		"📝 Описание: Поделитесь своим ПП рецептом\n\n"
		"<b>3. #тренировкадома</b>\n"
		"📅 До 20 декабря\n"
		"👥 890 участников\n"
		"🏆 Приз: Коврик для йоги\n"
		"📝 Описание: Покажите домашнюю тренировку\n\n"
		"<b>4. #прогрессзамесяц</b>\n"
		"📅 До 15 января\n"
		"👥 2,345 участников\n"
		"🏆 Приз: Умные часы\n"
		"📝 Описание: Покажите прогресс за месяц"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🏆 Участвовать в челлендже", callback_data="participate_challenge")],
		[InlineKeyboardButton(text="📊 Мои челленджи", callback_data="my_challenges")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "participate_challenge")
async def participate_challenge(callback: types.CallbackQuery, state: FSMContext):
	"""Участвовать в челлендже"""
	text = (
		"🏆 <b>Участие в челлендже</b>\n\n"
		"<b>Как участвовать:</b>\n\n"
		"1. Выберите челлендж\n"
		"2. Следуйте правилам\n"
		"3. Публикуйте фото/видео\n"
		"4. Используйте хештег\n"
		"5. Отмечайте @FitCoachBot\n\n"
		"<b>Требования к публикациям:</b>\n"
		"• Качественные фото/видео\n"
		"• Соответствие теме челленджа\n"
		"• Использование хештега\n"
		"• Отметка бота\n\n"
		"<b>Призы:</b>\n"
		"• Лучшие работы получают призы\n"
		"• Звезды за участие\n"
		"• Возможность попасть в топ\n\n"
		"Выберите челлендж для участия:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="💪 #30днейприседаний", callback_data="challenge_squats")],
		[InlineKeyboardButton(text="🍽️ #ппрецептынедели", callback_data="challenge_recipes")],
		[InlineKeyboardButton(text="🏠 #тренировкадома", callback_data="challenge_home")],
		[InlineKeyboardButton(text="📈 #прогрессзамесяц", callback_data="challenge_progress")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram_challenges")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("challenge_"))
async def select_challenge(callback: types.CallbackQuery, state: FSMContext):
	"""Выбор челленджа"""
	challenge_type = callback.data.split("_")[1]
	
	challenge_info = {
		'squats': {
			'name': '#30днейприседаний',
			'description': '30 дней приседаний с увеличением количества',
			'prize': 'Беспроводные наушники',
			'hashtag': '#30днейприседаний #FitCoachBot',
			'deadline': '31 декабря'
		},
		'recipes': {
			'name': '#ппрецептынедели',
			'description': 'Поделитесь своим ПП рецептом',
			'prize': 'Набор специй',
			'hashtag': '#ппрецептынедели #FitCoachBot',
			'deadline': '25 декабря'
		},
		'home': {
			'name': '#тренировкадома',
			'description': 'Покажите домашнюю тренировку',
			'prize': 'Коврик для йоги',
			'hashtag': '#тренировкадома #FitCoachBot',
			'deadline': '20 декабря'
		},
		'progress': {
			'name': '#прогрессзамесяц',
			'description': 'Покажите прогресс за месяц',
			'prize': 'Умные часы',
			'hashtag': '#прогрессзамесяц #FitCoachBot',
			'deadline': '15 января'
		}
	}
	
	challenge = challenge_info[challenge_type]
	
	text = (
		f"🏆 <b>Челлендж: {challenge['name']}</b>\n\n"
		f"<b>Описание:</b>\n{challenge['description']}\n\n"
		f"<b>Приз:</b> {challenge['prize']}\n"
		f"<b>Дедлайн:</b> {challenge['deadline']}\n\n"
		f"<b>Правила участия:</b>\n"
		f"1. Публикуйте фото/видео в Instagram\n"
		f"2. Используйте хештеги: {challenge['hashtag']}\n"
		f"3. Отмечайте @FitCoachBot\n"
		f"4. Следуйте теме челленджа\n\n"
		f"<b>Критерии оценки:</b>\n"
		"• Качество контента\n"
		"• Соответствие теме\n"
		"• Креативность\n"
		"• Регулярность участия\n\n"
		f"<b>Награды:</b>\n"
		"• Главный приз: {challenge['prize']}\n"
		"• Звезды за участие: +50 ⭐\n"
		"• Возможность попасть в топ"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📲 Перейти в Instagram", url="https://instagram.com/fitcoach_bot")],
		[InlineKeyboardButton(text="✅ Я участвую", callback_data=f"confirm_challenge:{challenge_type}")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="participate_challenge")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data.startswith("confirm_challenge:"))
async def confirm_challenge(callback: types.CallbackQuery, state: FSMContext):
	"""Подтверждение участия в челлендже"""
	challenge_type = callback.data.split(":")[1]
	
	challenge_names = {
		'squats': '#30днейприседаний',
		'recipes': '#ппрецептынедели',
		'home': '#тренировкадома',
		'progress': '#прогрессзамесяц'
	}
	
	text = (
		f"✅ <b>Участие подтверждено!</b>\n\n"
		f"<b>Челлендж:</b> {challenge_names[challenge_type]}\n"
		f"<b>Статус:</b> Активный участник\n"
		f"<b>Награда за участие:</b> +50 ⭐\n\n"
		f"<b>Что дальше:</b>\n"
		"1. Перейдите в Instagram\n"
		"2. Публикуйте контент по теме\n"
		"3. Используйте хештеги\n"
		"4. Отмечайте @FitCoachBot\n"
		"5. Следите за обновлениями\n\n"
		f"<b>Удачи в челлендже! 🏆</b>"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📲 Перейти в Instagram", url="https://instagram.com/fitcoach_bot")],
		[InlineKeyboardButton(text="📊 Мои челленджи", callback_data="my_challenges")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram_challenges")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "my_challenges")
async def my_challenges(callback: types.CallbackQuery, state: FSMContext):
	"""Мои челленджи"""
	text = (
		"📊 <b>Мои челленджи</b>\n\n"
		"<b>Активные участия:</b>\n\n"
		"<b>1. #30днейприседаний</b>\n"
		"📅 Участвую с 1 декабря\n"
		"📸 Публикаций: 15/30\n"
		"⭐ Звезд заработано: 25\n"
		"🏆 Шанс на приз: Высокий\n\n"
		"<b>2. #ппрецептынедели</b>\n"
		"📅 Участвую с 5 декабря\n"
		"📸 Публикаций: 3/7\n"
		"⭐ Звезд заработано: 15\n"
		"🏆 Шанс на приз: Средний\n\n"
		"<b>Завершенные:</b>\n\n"
		"<b>3. #тренировкадома (ноябрь)</b>\n"
		"📅 Участвовал 1-30 ноября\n"
		"📸 Публикаций: 28/30\n"
		"⭐ Звезд заработано: 50\n"
		"🏆 Результат: 3 место\n\n"
		"<b>Общая статистика:</b>\n"
		"• Всего челленджей: 3\n"
		"• Звезд заработано: 90 ⭐\n"
		"• Лучший результат: 3 место"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🏆 Участвовать в новом", callback_data="participate_challenge")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram_challenges")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "instagram_motivation")
async def instagram_motivation(callback: types.CallbackQuery, state: FSMContext):
	"""Мотивационные посты из Instagram"""
	text = (
		"💪 <b>Мотивация из Instagram</b>\n\n"
		"<b>Последние мотивационные посты:</b>\n\n"
		"<b>1. \"Каждый день - это новая возможность стать лучше\"</b>\n"
		"📅 2 часа назад\n"
		"❤️ 5,234 лайка\n"
		"💬 234 комментария\n\n"
		"<b>2. \"Прогресс, а не совершенство\"</b>\n"
		"📅 6 часов назад\n"
		"❤️ 3,567 лайка\n"
		"💬 156 комментариев\n\n"
		"<b>3. \"Тренировка - это инвестиция в себя\"</b>\n"
		"📅 1 день назад\n"
		"❤️ 4,890 лайка\n"
		"💬 189 комментариев\n\n"
		"<b>4. \"Маленькие шаги ведут к большим результатам\"</b>\n"
		"📅 2 дня назад\n"
		"❤️ 6,123 лайка\n"
		"💬 267 комментариев\n\n"
		"<b>5. \"Сегодня я выбираю быть сильнее вчерашнего себя\"</b>\n"
		"📅 3 дня назад\n"
		"❤️ 7,456 лайка\n"
		"💬 345 комментариев"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔄 Обновить", callback_data="instagram_motivation")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "instagram_recipes")
async def instagram_recipes(callback: types.CallbackQuery, state: FSMContext):
	"""Рецепты из Instagram"""
	text = (
		"🍽️ <b>Рецепты из Instagram</b>\n\n"
		"<b>Последние рецепты:</b>\n\n"
		"<b>1. 🥗 ПП салат с авокадо</b>\n"
		"📅 3 часа назад\n"
		"❤️ 2,345 лайка\n"
		"💬 123 комментария\n"
		"📝 Быстрый и полезный салат\n\n"
		"<b>2. 🍗 Куриная грудка в духовке</b>\n"
		"📅 8 часов назад\n"
		"❤️ 3,678 лайка\n"
		"💬 234 комментария\n"
		"📝 Нежная и сочная грудка\n\n"
		"<b>3. 🥑 Тост с авокадо и яйцом</b>\n"
		"📅 1 день назад\n"
		"❤️ 4,567 лайка\n"
		"💬 189 комментариев\n"
		"📝 Идеальный завтрак\n\n"
		"<b>4. 🥜 Протеиновые батончики</b>\n"
		"📅 2 дня назад\n"
		"❤️ 5,234 лайка\n"
		"💬 267 комментариев\n"
		"📝 Домашние ПП батончики\n\n"
		"<b>5. 🥤 Смузи с протеином</b>\n"
		"📅 3 дня назад\n"
		"❤️ 3,890 лайка\n"
		"💬 156 комментариев\n"
		"📝 Вкусный протеиновый коктейль"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔄 Обновить", callback_data="instagram_recipes")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "instagram_workouts")
async def instagram_workouts(callback: types.CallbackQuery, state: FSMContext):
	"""Тренировки из Instagram"""
	text = (
		"🏋️ <b>Тренировки из Instagram</b>\n\n"
		"<b>Последние тренировки:</b>\n\n"
		"<b>1. 💪 Тренировка ног дома</b>\n"
		"📅 4 часа назад\n"
		"❤️ 3,456 лайка\n"
		"💬 178 комментариев\n"
		"⏱️ 25 минут\n"
		"📝 Без инвентаря\n\n"
		"<b>2. 🏃 Кардио тренировка</b>\n"
		"📅 10 часов назад\n"
		"❤️ 4,789 лайка\n"
		"💬 234 комментария\n"
		"⏱️ 30 минут\n"
		"📝 HIIT тренировка\n\n"
		"<b>3. 🧘 Йога для начинающих</b>\n"
		"📅 1 день назад\n"
		"❤️ 5,234 лайка\n"
		"💬 189 комментариев\n"
		"⏱️ 20 минут\n"
		"📝 Растяжка и расслабление\n\n"
		"<b>4. 💪 Тренировка рук</b>\n"
		"📅 2 дня назад\n"
		"❤️ 3,890 лайка\n"
		"💬 156 комментариев\n"
		"⏱️ 35 минут\n"
		"📝 С гантелями\n\n"
		"<b>5. 🏃‍♀️ Плиометрика</b>\n"
		"📅 3 дня назад\n"
		"❤️ 4,567 лайка\n"
		"💬 223 комментария\n"
		"⏱️ 40 минут\n"
		"📝 Взрывные упражнения"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔄 Обновить", callback_data="instagram_workouts")],
		[InlineKeyboardButton(text="📲 Перейти в Instagram", callback_data="go_to_instagram")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "go_to_instagram")
async def go_to_instagram(callback: types.CallbackQuery, state: FSMContext):
	"""Перейти в Instagram"""
	text = (
		"📲 <b>Перейти в Instagram</b>\n\n"
		"<b>Наш Instagram профиль:</b>\n"
		"@FitCoachBot\n\n"
		"<b>Что вы найдете:</b>\n"
		"• Ежедневные мотивационные посты\n"
		"• Рецепты ПП блюд\n"
		"• Видео тренировок\n"
		"• Советы по питанию\n"
		"• Результаты пользователей\n"
		"• Челенджи и конкурсы\n"
		"• Прямые эфиры с тренерами\n\n"
		"<b>Подписывайтесь и будьте в курсе!</b>"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📱 Открыть Instagram", url="https://instagram.com/fitcoach_bot")],
		[InlineKeyboardButton(text="📸 Посмотреть Stories", url="https://instagram.com/fitcoach_bot")],
		[InlineKeyboardButton(text="📺 Прямые эфиры", url="https://instagram.com/fitcoach_bot")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="instagram")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "instagram")
async def back_to_instagram(callback: types.CallbackQuery):
	"""Возврат в главное меню Instagram"""
	await show_instagram_menu(callback.message)
	await callback.answer()


# Функция для автоматического репоста постов из Instagram
async def auto_repost_instagram_posts():
	"""
	Автоматический репост постов из Instagram
	В реальном проекте здесь должна быть логика:
	1. Получение постов через Instagram API
	2. Фильтрация по хештегам и темам
	3. Отправка в бота пользователям
	4. Логирование репостов
	"""
	pass


# Функция для мониторинга челленджей
async def monitor_instagram_challenges():
	"""
	Мониторинг Instagram челленджей
	В реальном проекте здесь должна быть логика:
	1. Отслеживание хештегов челленджей
	2. Подсчет участников
	3. Определение победителей
	4. Награждение звездами
	"""
	pass


# Функция для анализа вовлеченности
async def analyze_instagram_engagement():
	"""
	Анализ вовлеченности в Instagram
	В реальном проекте здесь должна быть логика:
	1. Подсчет лайков и комментариев
	2. Анализ роста подписчиков
	3. Определение популярного контента
	4. Генерация отчетов
	"""
	pass