from aiogram import Router, types

router = Router()


@router.message()
async def fallback(message: types.Message):
	text = (
		"Я помогу тебе подобрать программу и питание.\n"
		"Нажми /start, чтобы начать."
	)
	# Не дублируем, если это команда
	if message.text and message.text.startswith("/"):
		return
	await message.answer(text)