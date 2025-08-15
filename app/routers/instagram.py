from aiogram import Router, types
from aiogram.filters import Command
from app.config import settings
import feedparser

router = Router()


@router.message(Command("instagram"))
async def instagram(message: types.Message):
	profile = getattr(settings, "instagram_profile_url", None) or "https://instagram.com"
	rss = getattr(settings, "instagram_rss_url", None)
	text = [f"Наш Instagram: {profile}"]
	if rss:
		try:
			feed = feedparser.parse(rss)
			items = feed.entries[:3]
			text.append("\nПоследние посты:")
			for it in items:
				text.append(f"• {it.title}")
		except Exception:
			pass
	await message.answer("\n".join(text))