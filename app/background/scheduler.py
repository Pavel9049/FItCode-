from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import random
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings

MOTIVATION = [
	"Сегодня — лучший день, чтобы начать!",
	"Маленькие шаги каждый день дают большой результат",
	"Твое тело заслуживает лучшего",
]

NUTRITION_TIPS = [
	"Пейте больше воды",
	"Добавляйте клетчатку в каждый прием пищи",
	"Старайтесь есть медленные углеводы",
]


async def send_broadcast(bot: Bot, chat_id: int, text: str) -> None:
	try:
		await bot.send_message(chat_id, text)
	except Exception:
		pass


def setup_scheduler(chat_ids_provider):
	scheduler = AsyncIOScheduler()

	async def job():
		bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		for chat_id in await chat_ids_provider():
			kind = random.choice(["motivation", "nutrition"])
			if kind == "motivation":
				text = random.choice(MOTIVATION)
			else:
				text = random.choice(NUTRITION_TIPS)
			await send_broadcast(bot, chat_id, text)
		await bot.session.close()

	scheduler.add_job(job, "interval", hours=settings.broadcast_interval_hours, next_run_time=datetime.utcnow() + timedelta(seconds=5))
	scheduler.start()
	return scheduler