import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from app.config import settings
from app.db.session import init_db
from app.routers import start as start_router
from app.routers import purchase as purchase_router
from app.routers import payments_gateway as payments_router
from app.routers import check_payment as check_payment_router
from app.routers import cabinet as cabinet_router
from app.routers import admin as admin_router


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

	await init_db()
	logger.info("DB initialized. Starting polling...")
	# На случай, если раньше был включён webhook
	try:
		await bot.delete_webhook(drop_pending_updates=True)
	except Exception:
		pass
	await dp.start_polling(bot)


def create_fastapi_app() -> FastAPI:
	app = FastAPI(title="FitCoach Webhooks")

	@app.get("/health")
	async def health():
		return {"status": "ok"}

	return app


if __name__ == "__main__":
	if settings.run_mode == "polling":
		asyncio.run(run_polling())
	else:
		# Запуск через uvicorn: uvicorn app.main:create_fastapi_app --factory --host 0.0.0.0 --port 8080
		app = create_fastapi_app()