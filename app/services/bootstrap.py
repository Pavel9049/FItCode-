from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Program


DEFAULT_PROGRAMS = [
	{"id": 1, "code": "beginner", "title": "Начинающий", "price_rub": 755, "description": "Базовые упражнения (по 5 на группу), видео, демо-доступ"},
	{"id": 2, "code": "novice", "title": "Новичок", "price_rub": 1750, "description": "10 упр./группа, 12 ПП блюд в неделю, еженедельные обновления"},
	{"id": 3, "code": "advanced", "title": "Продвинутый", "price_rub": 2750, "description": "15 упр., функциональные, йога, растяжка, персональное питание, меню всех ПП"},
	{"id": 4, "code": "pro", "title": "Профессионал", "price_rub": 3050, "description": "20 упр., сплиты, 24/7 поддержка, кардио, AI, персональное питание, меню всех ПП, +10 звёзд"},
]


async def ensure_default_programs(session: AsyncSession) -> None:
	for p in DEFAULT_PROGRAMS:
		exists = (await session.execute(select(Program).where(Program.code == p["code"])) ).scalar_one_or_none()
		if not exists:
			session.add(Program(**p))
	await session.commit()