from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart
from app.services.programs import get_paid_programs

router = Router()


@router.message(CommandStart())
async def on_start(message: types.Message):
	text = (
		"Привет! Я — твой личный фитнес-тренер и нутрициолог.\n\n"
		"Здесь ты найдёшь:\n"
		"✅ Уникальные тренировки под каждый уровень\n"
		"✅ Персональное питание с КБЖУ и рецептами\n"
		"✅ Еженедельные обновления\n"
		"✅ Система звёзд и реальные призы\n"
		"✅ Поддержка целей и фото-отчётов\n\n"
		"Почему мы?\n"
		"🔹 Упражнения не повторяются (кроме начальных уровней)\n"
		"🔹 Подбор под твою цель\n"
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
	lines = []
	for p in programs:
		features = "\n".join([f"• {f}" for f in p["features"]])
		lines.append(f"{p['title']} — {p['price_rub']} ₽\n{features}\n")
	text = "\n".join(lines)

	# Кнопки покупки
	buttons = [
		[InlineKeyboardButton(text=f"Купить: {p['title']}", callback_data=f"buy:{p['code']}")]
		for p in programs
	]
	kb = InlineKeyboardMarkup(inline_keyboard=buttons)
	await callback.message.edit_text(text)
	await callback.message.edit_reply_markup(kb)
	await callback.answer()