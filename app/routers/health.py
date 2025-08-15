from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("ping"))
async def ping(message: types.Message):
	await message.answer("pong")


@router.message(Command("help"))
async def help_cmd(message: types.Message):
	await message.answer(
		"Команды:\n"
		"/start — начать\n"
		"/cabinet — личный кабинет\n"
		"/workouts — тренировки\n"
		"/menu — меню на неделю\n"
		"/kbju — AI КБЖУ\n"
		"/rewards — звёзды и призы\n"
		"/settings — настройки\n"
		"/instagram — Instagram\n"
		"/ref — реферальная ссылка\n"
		"/support — поддержка (PRO)\n"
		"/ping — проверка связи"
	)