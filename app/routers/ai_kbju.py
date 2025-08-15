from aiogram import Router, types
from aiogram.filters import Command
from app.services.ai_kbju import estimate_kbju_from_photo

router = Router()


@router.message(Command("kbju"))
async def kbju_hint(message: types.Message):
	await message.answer("Отправьте фото блюда и я оценю КБЖУ (оценка приблизительная)")


@router.message(lambda m: m.photo)
async def kbju_photo(message: types.Message):
	photo = message.photo[-1]
	file = await message.bot.get_file(photo.file_id)
	file_bytes = await message.bot.download_file(file.file_path)
	kbju = await estimate_kbju_from_photo(file_bytes.read())
	await message.answer(f"Оценка: {kbju['kcal']} ккал / {kbju['proteins']}Б / {kbju['fats']}Ж / {kbju['carbs']}У\nМетка: оценка приблизительная")