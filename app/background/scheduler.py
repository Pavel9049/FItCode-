from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import random
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.utils.broadcast_utils import BroadcastManager

MOTIVATION = [
	"💪 Сегодня — лучший день, чтобы начать!",
	"🔥 Маленькие шаги каждый день дают большой результат",
	"⭐ Твое тело заслуживает лучшего",
	"🏃‍♂️ Прогресс — это не всегда быстро, но он всегда постоянен",
	"🎯 Цель без плана — это просто желание",
	"💎 Алмаз создается под давлением, так же как и чемпион",
	"🚀 Не останавливайся, когда устал. Останавливайся, когда закончил",
	"🌟 Ты сильнее, чем думаешь, и способнее, чем можешь представить",
	"🔥 Каждый день — это новая возможность стать лучше",
	"💪 Тренировки не делают дни легче, они делают тебя сильнее",
	"🎯 Маленькие шаги каждый день приводят к большим изменениям",
	"⭐ Ты не проигрываешь, пока не сдаешься",
	"🏋️‍♂️ Сила приходит не от физических способностей, а от несгибаемой воли",
	"🔥 Будь тем изменением, которое ты хочешь видеть в себе",
	"💎 Трудности — это возможности в рабочей одежде"
]

NUTRITION_TIPS = [
	"💧 Пейте больше воды — минимум 2 литра в день",
	"🥬 Добавляйте клетчатку в каждый прием пищи",
	"🌾 Старайтесь есть медленные углеводы",
	"🥩 Не забывайте про белок — он важен для мышц",
	"🥑 Включайте полезные жиры в рацион",
	"🍎 Ешьте больше овощей и фруктов",
	"⏰ Старайтесь есть в одно и то же время",
	"🍽️ Не пропускайте приемы пищи",
	"🥛 Включайте молочные продукты в рацион",
	"🌰 Добавляйте орехи и семена",
	"🐟 Ешьте рыбу минимум 2 раза в неделю",
	"🥚 Яйца — отличный источник белка",
	"🍠 Сладкий картофель — полезная альтернатива обычному",
	"🥦 Брокколи богата витаминами и минералами",
	"🍓 Ягоды — природные антиоксиданты"
]

WORKOUT_TIPS = [
	"🏋️‍♂️ Начинайте тренировку с разминки",
	"💪 Делайте упражнения медленно и контролируемо",
	"🔄 Не забывайте про растяжку после тренировки",
	"📊 Ведите дневник тренировок",
	"🎯 Ставьте конкретные цели",
	"⏰ Тренируйтесь в одно и то же время",
	"🛌 Давайте мышцам время на восстановление",
	"💧 Пейте воду во время тренировки",
	"🎵 Слушайте мотивирующую музыку",
	"👥 Найдите партнера для тренировок",
	"📱 Используйте фитнес-приложения для отслеживания",
	"🏃‍♂️ Включайте кардио в программу",
	"💪 Работайте над всеми группами мышц",
	"🎯 Фокусируйтесь на технике выполнения",
	"⭐ Не сравнивайте себя с другими"
]


async def send_broadcast(bot: Bot, chat_id: int, text: str) -> None:
	try:
		await bot.send_message(chat_id, text)
	except Exception:
		pass


def setup_scheduler(chat_ids_provider):
	scheduler = AsyncIOScheduler()

	async def motivation_job():
		"""Мотивационные сообщения каждые 4 часа"""
		bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		text = random.choice(MOTIVATION)
		for chat_id in await chat_ids_provider():
			await send_broadcast(bot, chat_id, text)
		await bot.session.close()

	async def nutrition_job():
		"""Советы по питанию каждые 6 часов"""
		bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		text = random.choice(NUTRITION_TIPS)
		for chat_id in await chat_ids_provider():
			await send_broadcast(bot, chat_id, text)
		await bot.session.close()

	async def workout_job():
		"""Советы по тренировкам каждые 8 часов"""
		bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		text = random.choice(WORKOUT_TIPS)
		for chat_id in await chat_ids_provider():
			await send_broadcast(bot, chat_id, text)
		await bot.session.close()

	async def star_reminder_job():
		"""Напоминание о звездах каждый день в 18:00"""
		bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		text = "⭐ Выполни тренировку — получи звезду!\n\nЗвезды можно обменять на реальные призы в разделе 'Звезды и призы'."
		for chat_id in await chat_ids_provider():
			await send_broadcast(bot, chat_id, text)
		await bot.session.close()

	async def progress_check_job():
		"""Напоминание о проверке прогресса каждое воскресенье"""
		bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		text = (
			"📊 <b>Время проверить прогресс!</b>\n\n"
			"Не забудьте:\n"
			"• Взвеситься\n"
			"• Сделать фото прогресса\n"
			"• Обновить цели\n\n"
			"Это поможет отследить результаты и получить звезды!"
		)
		for chat_id in await chat_ids_provider():
			await send_broadcast(bot, chat_id, text)
		await bot.session.close()

	# Добавляем задачи в планировщик
	scheduler.add_job(motivation_job, "interval", hours=4, next_run_time=datetime.utcnow() + timedelta(seconds=5))
	scheduler.add_job(nutrition_job, "interval", hours=6, next_run_time=datetime.utcnow() + timedelta(seconds=10))
	scheduler.add_job(workout_job, "interval", hours=8, next_run_time=datetime.utcnow() + timedelta(seconds=15))
	scheduler.add_job(star_reminder_job, "cron", hour=18, minute=0, next_run_time=datetime.utcnow() + timedelta(seconds=20))
	scheduler.add_job(progress_check_job, "cron", day_of_week="sun", hour=10, minute=0, next_run_time=datetime.utcnow() + timedelta(seconds=25))
	
	scheduler.start()
	return scheduler