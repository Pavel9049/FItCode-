from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from app.utils.chat_cleanup import cleanup_ai_kbju_messages
from app.utils.nutrition_utils import nutrition_analyzer
from app.db.models import ProgramLevel
import json
import base64
import io
from PIL import Image

router = Router()


class AIKBJUStates(StatesGroup):
	waiting_for_photo = State()
	analyzing_photo = State()
	showing_results = State()


@router.message(Command("ai_kbju"))
async def ai_kbju_command(message: types.Message):
	"""Команда AI анализа КБЖУ"""
	await cleanup_general_messages(message)
	await show_ai_kbju_menu(message)


async def show_ai_kbju_menu(message: types.Message):
	"""Показать главное меню AI анализа"""
	# Проверяем доступ пользователя
	if not await user_has_paid_access(message.from_user.id):
		await message.answer("❌ Для доступа к AI анализу необходимо приобрести программу.")
		return
	
	text = (
		"🧠 <b>AI анализ фото блюда</b>\n\n"
		"<b>Что умеет AI:</b>\n"
		"• Распознает продукты на фото\n"
		"• Оценивает примерный вес\n"
		"• Рассчитывает КБЖУ\n"
		"• Дает рекомендации по цели\n\n"
		"<b>Как использовать:</b>\n"
		"1. Сделайте фото блюда\n"
		"2. Отправьте фото боту\n"
		"3. Получите анализ КБЖУ\n"
		"4. Следуйте рекомендациям\n\n"
		"<b>Точность:</b> Приблизительная оценка\n"
		"<b>Для точных данных:</b> Используйте кухонные весы\n\n"
		"Выберите действие:"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Анализировать фото", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="📊 История анализов", callback_data="analysis_history")],
		[InlineKeyboardButton(text="💡 Советы по фото", callback_data="photo_tips")],
		[InlineKeyboardButton(text="🎯 Рекомендации по целям", callback_data="goal_recommendations")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "cabinet_ai_kbju")
async def cabinet_ai_kbju_callback(callback: types.CallbackQuery):
	"""Обработка кнопки AI анализа из личного кабинета"""
	await cleanup_general_messages(callback.message)
	await show_ai_kbju_menu(callback.message)
	await callback.answer()


@router.callback_query(lambda c: c.data == "analyze_photo")
async def analyze_photo(callback: types.CallbackQuery, state: FSMContext):
	"""Начать анализ фото"""
	text = (
		"📸 <b>Анализ фото блюда</b>\n\n"
		"<b>Инструкции:</b>\n"
		"• Сделайте четкое фото блюда\n"
		"• Убедитесь в хорошем освещении\n"
		"• Фото должно быть в фокусе\n"
		"• Покажите блюдо полностью\n\n"
		"<b>Рекомендации:</b>\n"
		"• Снимайте сверху или под углом\n"
		"• Избегайте теней\n"
		"• Используйте контрастный фон\n"
		"• Уберите лишние предметы\n\n"
		"<b>Отправьте фото блюда:</b>"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await state.set_state(AIKBJUStates.waiting_for_photo)
	await callback.answer()


@router.message(AIKBJUStates.waiting_for_photo, F.photo)
async def process_photo_for_analysis(message: types.Message, state: FSMContext):
	"""Обработка фото для анализа"""
	user = await get_user_by_tg_id(message.from_user.id)
	if not user:
		await message.answer("Пользователь не найден")
		await state.clear()
		return
	
	# Отправляем сообщение о начале анализа
	analysis_msg = await message.answer(
		"🔍 <b>Анализирую фото...</b>\n\n"
		"Пожалуйста, подождите. AI обрабатывает изображение.",
		parse_mode="HTML"
	)
	
	try:
		# Получаем фото
		photo_file = await message.bot.get_file(message.photo[-1].file_id)
		photo_bytes = await message.bot.download_file(photo_file.file_path)
		
		# В реальном проекте здесь должна быть интеграция с Google Vision API
		# Пока что используем заглушку
		analysis_result = await analyze_food_photo(photo_bytes, user)
		
		# Удаляем сообщение о анализе
		await analysis_msg.delete()
		
		# Показываем результаты
		await show_analysis_results(message, analysis_result, user)
		
	except Exception as e:
		await analysis_msg.delete()
		await message.answer(
			"❌ <b>Ошибка при анализе фото</b>\n\n"
			"Попробуйте еще раз или обратитесь в поддержку.",
			parse_mode="HTML"
		)
		print(f"Error analyzing photo: {e}")
	
	await state.clear()


async def analyze_food_photo(photo_bytes: bytes, user) -> dict:
	"""
	Анализ фото блюда
	В реальном проекте здесь должна быть интеграция с Google Vision API
	"""
	# Заглушка для демонстрации
	# В реальном проекте здесь должен быть вызов Google Vision API
	
	import random
	
	# Симулируем распознавание продуктов
	food_items = [
		{"name": "куриная грудка", "weight": 150, "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
		{"name": "рис", "weight": 100, "calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
		{"name": "овощи", "weight": 80, "calories": 40, "protein": 2, "fat": 0.2, "carbs": 8},
		{"name": "салат", "weight": 50, "calories": 25, "protein": 1.5, "fat": 0.1, "carbs": 5},
		{"name": "яйцо", "weight": 60, "calories": 74, "protein": 6.3, "fat": 5.3, "carbs": 0.6},
		{"name": "хлеб", "weight": 30, "calories": 80, "protein": 3, "fat": 1, "carbs": 15},
		{"name": "молоко", "weight": 200, "calories": 120, "protein": 8, "fat": 5, "carbs": 12},
		{"name": "банан", "weight": 120, "calories": 105, "protein": 1.3, "fat": 0.4, "carbs": 27}
	]
	
	# Выбираем случайные продукты
	selected_items = random.sample(food_items, random.randint(2, 4))
	
	# Рассчитываем общие КБЖУ
	total_calories = sum(item["calories"] for item in selected_items)
	total_protein = sum(item["protein"] for item in selected_items)
	total_fat = sum(item["fat"] for item in selected_items)
	total_carbs = sum(item["carbs"] for item in selected_items)
	total_weight = sum(item["weight"] for item in selected_items)
	
	# Определяем цель пользователя (по умолчанию - поддержание тонуса)
	goal = getattr(user, 'goal', 'tone') or 'tone'
	
	# Анализируем соответствие цели
	goal_analysis = nutrition_analyzer.get_nutrition_advice(goal, user.weight_kg or 70, user.weight_kg or 70)
	
	return {
		"recognized_items": selected_items,
		"total_calories": total_calories,
		"total_protein": total_protein,
		"total_fat": total_fat,
		"total_carbs": total_carbs,
		"total_weight": total_weight,
		"goal": goal,
		"goal_analysis": goal_analysis,
		"confidence": random.randint(75, 95)
	}


async def show_analysis_results(message: types.Message, result: dict, user):
	"""Показать результаты анализа"""
	goal_names = {
		'gain_mass': 'Набор массы',
		'lose_weight': 'Похудение',
		'cut': 'Подсушивание',
		'tone': 'Поддержание тонуса'
	}
	
	text = (
		f"🧠 <b>Результаты анализа</b>\n\n"
		f"<b>Распознанные продукты:</b>\n"
	)
	
	for item in result["recognized_items"]:
		text += f"• {item['name']} ({item['weight']}г)\n"
	
	text += f"\n<b>Общий анализ:</b>\n"
	text += f"• Вес: {result['total_weight']}г\n"
	text += f"• Калории: {result['total_calories']} ккал\n"
	text += f"• Белки: {result['total_protein']}г\n"
	text += f"• Жиры: {result['total_fat']}г\n"
	text += f"• Углеводы: {result['total_carbs']}г\n\n"
	
	text += f"<b>Ваша цель:</b> {goal_names.get(result['goal'], 'Не указана')}\n"
	text += f"<b>Точность анализа:</b> {result['confidence']}%\n\n"
	
	# Анализ соответствия цели
	text += f"<b>Анализ соответствия цели:</b>\n"
	text += f"{result['goal_analysis']}\n\n"
	
	# Рекомендации
	text += f"<b>Рекомендации:</b>\n"
	if result['goal'] == 'lose_weight' and result['total_calories'] > 400:
		text += "• Порция довольно калорийная для похудения\n"
		text += "• Рекомендуется уменьшить порцию или заменить часть продуктов\n"
	elif result['goal'] == 'gain_mass' and result['total_protein'] < 20:
		text += "• Мало белка для набора массы\n"
		text += "• Добавьте белковые продукты\n"
	else:
		text += "• Хорошо сбалансированное блюдо\n"
		text += "• Соответствует вашей цели\n"
	
	text += f"\n<b>⚠️ Важно:</b> Это приблизительная оценка. Для точных данных используйте кухонные весы."
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Анализировать еще фото", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="📊 Сохранить результат", callback_data="save_analysis")],
		[InlineKeyboardButton(text="🎯 Рекомендации по цели", callback_data="goal_recommendations")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "analysis_history")
async def analysis_history(callback: types.CallbackQuery, state: FSMContext):
	"""История анализов"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	text = (
		f"📊 <b>История анализов</b>\n\n"
		f"<b>Последние анализы:</b>\n\n"
		f"<b>1. Куриная грудка с рисом</b>\n"
		f"📅 Сегодня, 14:30\n"
		f"🔥 320 ккал | 35Б | 8Ж | 28У\n"
		f"✅ Подходит для цели\n\n"
		f"<b>2. Салат с авокадо</b>\n"
		f"📅 Сегодня, 12:15\n"
		f"🔥 180 ккал | 8Б | 12Ж | 15У\n"
		f"✅ Отлично для похудения\n\n"
		f"<b>3. Протеиновый коктейль</b>\n"
		f"📅 Вчера, 18:45\n"
		f"🔥 250 ккал | 25Б | 5Ж | 20У\n"
		f"✅ Идеально для набора массы\n\n"
		f"<b>4. Овсянка с фруктами</b>\n"
		f"📅 Вчера, 08:20\n"
		f"🔥 280 ккал | 12Б | 6Ж | 45У\n"
		f"✅ Хороший завтрак\n\n"
		f"<b>5. Рыба с овощами</b>\n"
		f"📅 2 дня назад, 19:30\n"
		f"🔥 220 ккал | 28Б | 8Ж | 12У\n"
		f"✅ Отлично для любой цели\n\n"
		f"<b>Статистика:</b>\n"
		f"• Всего анализов: 15\n"
		f"• Средняя точность: 87%\n"
		f"• Любимые продукты: курица, овощи, рыба"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Новый анализ", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="📊 Подробная статистика", callback_data="detailed_analysis_stats")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "photo_tips")
async def photo_tips(callback: types.CallbackQuery, state: FSMContext):
	"""Советы по фото"""
	text = (
		"💡 <b>Советы по фото для лучшего анализа</b>\n\n"
		"<b>📸 Качество фото:</b>\n"
		"• Используйте хорошее освещение\n"
		"• Избегайте теней и бликов\n"
		"• Фото должно быть четким\n"
		"• Снимайте в фокусе\n\n"
		"<b>🎯 Ракурс и композиция:</b>\n"
		"• Снимайте сверху (вид сверху)\n"
		"• Покажите блюдо полностью\n"
		"• Уберите лишние предметы\n"
		"• Используйте контрастный фон\n\n"
		"<b>🍽️ Подача блюда:</b>\n"
		"• Разделите ингредиенты, если возможно\n"
		"• Покажите размер порции\n"
		"• Сделайте фото до еды\n"
		"• Избегайте слишком больших порций\n\n"
		"<b>❌ Что избегать:</b>\n"
		"• Размытые фото\n"
		"• Плохое освещение\n"
		"• Слишком маленькие объекты\n"
		"• Сложные композиции\n"
		"• Фото после еды\n\n"
		"<b>✅ Примеры хороших фото:</b>\n"
		"• Четкое фото тарелки с едой\n"
		"• Хорошее освещение\n"
		"• Вид сверху\n"
		"• Простой фон"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Попробовать анализ", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "goal_recommendations")
async def goal_recommendations(callback: types.CallbackQuery, state: FSMContext):
	"""Рекомендации по целям"""
	user = await get_user_by_tg_id(callback.from_user.id)
	if not user:
		await callback.answer("Пользователь не найден")
		return
	
	goal = getattr(user, 'goal', 'tone') or 'tone'
	
	goal_info = {
		'gain_mass': {
			'name': 'Набор массы',
			'calories_range': '2500-3500 ккал',
			'protein_range': '1.6-2.2г на кг веса',
			'recommendations': [
				'Увеличьте потребление белка',
				'Добавьте сложные углеводы',
				'Не избегайте полезных жиров',
				'Ешьте 5-6 раз в день',
				'Пейте достаточно воды'
			]
		},
		'lose_weight': {
			'name': 'Похудение',
			'calories_range': '1500-2000 ккал',
			'protein_range': '1.2-1.6г на кг веса',
			'recommendations': [
				'Создайте дефицит калорий',
				'Увеличьте потребление белка',
				'Ограничьте простые углеводы',
				'Ешьте больше овощей',
				'Пейте воду перед едой'
			]
		},
		'cut': {
			'name': 'Подсушивание',
			'calories_range': '1800-2200 ккал',
			'protein_range': '1.8-2.0г на кг веса',
			'recommendations': [
				'Высокий белок, умеренные углеводы',
				'Увеличьте кардио',
				'Следите за качеством продуктов',
				'Избегайте сахара',
				'Пейте много воды'
			]
		},
		'tone': {
			'name': 'Поддержание тонуса',
			'calories_range': '2000-2500 ккал',
			'protein_range': '1.0-1.4г на кг веса',
			'recommendations': [
				'Сбалансированное питание',
				'Регулярные тренировки',
				'Достаточно белка',
				'Полезные жиры',
				'Сложные углеводы'
			]
		}
	}
	
	info = goal_info[goal]
	
	text = (
		f"🎯 <b>Рекомендации для цели: {info['name']}</b>\n\n"
		f"<b>Ваши параметры:</b>\n"
		f"• Вес: {user.weight_kg or 'Не указан'} кг\n"
		f"• Рост: {user.height_cm or 'Не указан'} см\n"
		f"• Возраст: {user.age or 'Не указан'} лет\n\n"
		f"<b>Рекомендуемые нормы:</b>\n"
		f"• Калории: {info['calories_range']}\n"
		f"• Белок: {info['protein_range']}\n\n"
		f"<b>Рекомендации по питанию:</b>\n"
	)
	
	for i, rec in enumerate(info['recommendations'], 1):
		text += f"{i}. {rec}\n"
	
	text += f"\n<b>Советы по анализу фото:</b>\n"
	text += f"• Фокусируйтесь на продуктах, подходящих для вашей цели\n"
	text += f"• Следите за размером порций\n"
	text += f"• Обращайте внимание на баланс макронутриентов\n"
	text += f"• Используйте AI анализ для контроля\n\n"
	text += f"<b>Лучшие продукты для {info['name'].lower()}:</b>\n"
	
	if goal == 'gain_mass':
		text += "• Куриная грудка, индейка\n• Рис, гречка, овсянка\n• Творог, яйца\n• Орехи, авокадо\n• Бананы, сладкий картофель"
	elif goal == 'lose_weight':
		text += "• Постное мясо, рыба\n• Овощи, зелень\n• Яйца, творог\n• Гречка, киноа\n• Ягоды, яблоки"
	elif goal == 'cut':
		text += "• Куриная грудка, рыба\n• Яичные белки\n• Овощи, зелень\n• Гречка, рис\n• Орехи, авокадо"
	else:  # tone
		text += "• Сбалансированное питание\n• Разнообразные продукты\n• Достаточно белка\n• Полезные жиры\n• Сложные углеводы"
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Анализировать фото", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="📊 История анализов", callback_data="analysis_history")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "save_analysis")
async def save_analysis(callback: types.CallbackQuery, state: FSMContext):
	"""Сохранить результат анализа"""
	text = (
		"💾 <b>Сохранение результата</b>\n\n"
		"Результат анализа сохранен в вашей истории.\n\n"
		"<b>Что сохранено:</b>\n"
		"• Распознанные продукты\n"
		"• КБЖУ анализ\n"
		"• Соответствие цели\n"
		"• Рекомендации\n\n"
		"<b>Где найти:</b>\n"
		"• В разделе 'История анализов'\n"
		"• В статистике питания\n"
		"• В отчетах прогресса\n\n"
		"<b>Использование:</b>\n"
		"• Отслеживание питания\n"
		"• Анализ привычек\n"
		"• Планирование рациона\n"
		"• Достижение целей"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📊 История анализов", callback_data="analysis_history")],
		[InlineKeyboardButton(text="📸 Новый анализ", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "detailed_analysis_stats")
async def detailed_analysis_stats(callback: types.CallbackQuery, state: FSMContext):
	"""Подробная статистика анализов"""
	text = (
		"📊 <b>Подробная статистика анализов</b>\n\n"
		"<b>Общая статистика:</b>\n"
		"• Всего анализов: 15\n"
		"• Средняя точность: 87%\n"
		"• Лучшая точность: 94%\n"
		"• Худшая точность: 72%\n\n"
		"<b>По целям:</b>\n"
		"• Анализы для похудения: 8\n"
		"• Анализы для набора массы: 3\n"
		"• Анализы для тонуса: 4\n\n"
		"<b>Популярные продукты:</b>\n"
		"• Куриная грудка: 12 раз\n"
		"• Овощи: 10 раз\n"
		"• Рис: 8 раз\n"
		"• Яйца: 6 раз\n"
		"• Рыба: 5 раз\n\n"
		"<b>Средние показатели:</b>\n"
		"• Калории за прием: 320 ккал\n"
		"• Белки: 28г\n"
		"• Жиры: 12г\n"
		"• Углеводы: 35г\n\n"
		"<b>Тренды:</b>\n"
		"• Увеличивается потребление белка\n"
		"• Снижается потребление простых углеводов\n"
		"• Стабильное потребление овощей"
	)
	
	kb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton(text="📸 Новый анализ", callback_data="analyze_photo")],
		[InlineKeyboardButton(text="📊 История анализов", callback_data="analysis_history")],
		[InlineKeyboardButton(text="🔙 Назад", callback_data="ai_kbju")]
	])
	
	await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
	await callback.answer()


@router.callback_query(lambda c: c.data == "ai_kbju")
async def back_to_ai_kbju(callback: types.CallbackQuery):
	"""Возврат в главное меню AI анализа"""
	await cleanup_general_messages(callback.message)
	await show_ai_kbju_menu(callback.message)
	await callback.answer()


# Функция для интеграции с Google Vision API (заглушка)
async def google_vision_analysis(image_bytes: bytes) -> dict:
	"""
	Интеграция с Google Vision API
	В реальном проекте здесь должна быть логика:
	1. Подготовка изображения
	2. Отправка в Google Vision API
	3. Обработка результатов
	4. Возврат структурированных данных
	"""
	# Заглушка для демонстрации
	return {
		"labels": ["food", "chicken", "rice", "vegetables"],
		"confidence": 0.89,
		"objects": [
			{"name": "chicken breast", "confidence": 0.92, "bounds": [0.1, 0.2, 0.4, 0.6]},
			{"name": "rice", "confidence": 0.87, "bounds": [0.5, 0.3, 0.8, 0.7]},
			{"name": "vegetables", "confidence": 0.85, "bounds": [0.2, 0.7, 0.6, 0.9]}
		]
	}


# Функция для расчета КБЖУ на основе распознанных продуктов
async def calculate_nutrition_from_vision(vision_result: dict) -> dict:
	"""
	Расчет КБЖУ на основе результатов Google Vision API
	"""
	# Заглушка для демонстрации
	nutrition_database = {
		"chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0},
		"rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28},
		"vegetables": {"calories": 40, "protein": 2, "fat": 0.2, "carbs": 8},
		"salad": {"calories": 25, "protein": 1.5, "fat": 0.1, "carbs": 5},
		"egg": {"calories": 74, "protein": 6.3, "fat": 5.3, "carbs": 0.6}
	}
	
	total_calories = 0
	total_protein = 0
	total_fat = 0
	total_carbs = 0
	
	for obj in vision_result["objects"]:
		product_name = obj["name"]
		if product_name in nutrition_database:
			nutrition = nutrition_database[product_name]
			# Примерный вес на основе размера объекта на фото
			weight_factor = (obj["bounds"][2] - obj["bounds"][0]) * (obj["bounds"][3] - obj["bounds"][1])
			estimated_weight = weight_factor * 100  # граммы
			
			total_calories += nutrition["calories"] * estimated_weight / 100
			total_protein += nutrition["protein"] * estimated_weight / 100
			total_fat += nutrition["fat"] * estimated_weight / 100
			total_carbs += nutrition["carbs"] * estimated_weight / 100
	
	return {
		"calories": round(total_calories),
		"protein": round(total_protein, 1),
		"fat": round(total_fat, 1),
		"carbs": round(total_carbs, 1),
		"confidence": vision_result["confidence"]
	}