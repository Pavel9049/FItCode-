import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from app.config import settings
from app.db.session import init_db, get_session_maker
from app.routers import start as start_router
from app.routers import purchase as purchase_router
from app.routers import payments_gateway as payments_router
from app.routers import check_payment as check_payment_router
from app.routers import cabinet as cabinet_router
from app.routers import admin as admin_router
from app.background.scheduler import setup_scheduler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_polling():
	bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()
	dp.include_router(start_router.router)
	dp.include_router(purchase_router.router)
	dp.include_router(payments_router.router)
	dp.include_router(check_payment_router.router)
	dp.include_router(cabinet_router.router)
	dp.include_router(admin_router.router)
	# Новые разделы
	from app.routers import workouts as workouts_router
	from app.routers import menu as menu_router
	from app.routers import ai_kbju as ai_kbju_router
	from app.routers import rewards as rewards_router
	from app.routers import settings as settings_router
	from app.routers import support as support_router
	from app.routers import instagram as instagram_router
	from app.routers import health as health_router
	dp.include_router(workouts_router.router)
	dp.include_router(menu_router.router)
	dp.include_router(ai_kbju_router.router)
	dp.include_router(rewards_router.router)
	dp.include_router(settings_router.router)
	dp.include_router(support_router.router)
	dp.include_router(instagram_router.router)
	dp.include_router(health_router.router)
	# Рефералы
	from app.routers import referral as referral_router
	dp.include_router(referral_router.router)
	# Фоллбек
	from app.routers import fallback as fallback_router
	dp.include_router(fallback_router.router)

	await init_db()
	logger.info("DB initialized. Starting polling...")
	# На случай, если раньше был включён webhook
	try:
		await bot.delete_webhook(drop_pending_updates=True)
	except Exception:
		pass

	# Команды бота
	from aiogram.types import BotCommand
	try:
		await bot.set_my_commands([
			BotCommand(command="start", description="Начать"),
			BotCommand(command="cabinet", description="Личный кабинет"),
			BotCommand(command="workouts", description="Тренировки"),
			BotCommand(command="menu", description="Меню на неделю (PDF)"),
			BotCommand(command="kbju", description="AI КБЖУ по фото"),
			BotCommand(command="rewards", description="Звезды и призы"),
			BotCommand(command="settings", description="Настройки уведомлений"),
			BotCommand(command="instagram", description="Instagram"),
			BotCommand(command="ref", description="Реферальная ссылка"),
			BotCommand(command="support", description="Поддержка 24/7 (PRO)"),
		])
	except Exception:
		pass

	# Планировщик рассылок
	if settings.scheduler_enabled:
		async def all_chat_ids():
			async_session = get_session_maker()
			async with async_session() as s:
				from sqlalchemy import select
				from app.db.models import User
				rows = (await s.execute(select(User.tg_user_id))).all()
				return [r[0] for r in rows if r[0]]
		setup_scheduler(all_chat_ids)

	await dp.start_polling(bot)


def create_fastapi_app() -> FastAPI:
	app = FastAPI(title="FitCoach Webhooks")

	@app.get("/health")
	async def health():
		return {"status": "ok"}

	# Webhooks
	from fastapi import Request, Response
	from app.db.session import get_session_maker
	from app.db.models import Purchase, User, Program
	from sqlalchemy import select, update
	import json

	@app.post("/webhooks/stripe")
	async def stripe_webhook(request: Request):
		payload = await request.body()
		sig = request.headers.get("Stripe-Signature")
		# В проде проверьте подпись
		data = await request.json()
		event_type = data.get("type")
		obj = data.get("data", {}).get("object", {})
		metadata = obj.get("metadata", {})
		purchase_id = metadata.get("purchase_id")
		if event_type in ("checkout.session.completed", "payment_intent.succeeded") and purchase_id:
			async_session = get_session_maker()
			async with async_session() as s:
				await s.execute(update(Purchase).where(Purchase.id == int(purchase_id)).values(paid=True))
				await s.commit()
		return Response(status_code=200)

	@app.post("/webhooks/yookassa")
	async def yookassa_webhook(request: Request):
		j = await request.json()
		event = j.get("event")
		obj = j.get("object", {})
		metadata = obj.get("metadata", {})
		purchase_id = metadata.get("purchase_id")
		if event == "payment.succeeded" and purchase_id:
			async_session = get_session_maker()
			async with async_session() as s:
				await s.execute(update(Purchase).where(Purchase.id == int(purchase_id)).values(paid=True))
				await s.commit()
		return Response(status_code=200)

	return app


if __name__ == "__main__":
	if settings.run_mode == "polling":
		asyncio.run(run_polling())
	else:
		# Запуск через uvicorn: uvicorn app.main:create_fastapi_app --factory --host 0.0.0.0 --port 8080
		app = create_fastapi_app()