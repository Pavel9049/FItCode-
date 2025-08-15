from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from aiogram import Bot
from app.db.session import get_session_maker
from app.db.models import User
from sqlalchemy import select
from app.utils.rewards_utils import motivation_manager


class BroadcastManager:
	"""Менеджер рассылок"""
	
	def __init__(self, bot: Bot):
		self.bot = bot
	
	async def send_motivational_message(self) -> int:
		"""Отправить мотивационное сообщение всем пользователям"""
		message = motivation_manager.get_daily_motivation()
		return await self._send_to_all_users(message)
	
	async def send_workout_reminder(self) -> int:
		"""Отправить напоминание о тренировке"""
		message = motivation_manager.get_workout_reminder()
		return await self._send_to_all_users(message)
	
	async def send_nutrition_tip(self) -> int:
		"""Отправить совет по питанию"""
		message = motivation_manager.get_random_nutrition_tip()
		return await self._send_to_all_users(message)
	
	async def send_workout_tip(self) -> int:
		"""Отправить совет по тренировкам"""
		message = motivation_manager.get_random_workout_tip()
		return await self._send_to_all_users(message)
	
	async def send_new_meal_announcement(self, meal_name: str) -> int:
		"""Отправить анонс нового блюда"""
		message = f"🍽️ <b>Новое блюдо в меню!</b>\n\n{meal_name}\n\nПопробуйте в разделе 'Меню на неделю'!"
		return await self._send_to_all_users(message, parse_mode="HTML")
	
	async def send_star_reminder(self) -> int:
		"""Отправить напоминание о звездах"""
		message = "⭐ Выполни тренировку — получи звезду!\n\nЗвезды можно обменять на реальные призы в разделе 'Звезды и призы'."
		return await self._send_to_all_users(message)
	
	async def send_weekly_progress_check(self) -> int:
		"""Отправить напоминание о проверке прогресса"""
		message = (
			"📊 <b>Время проверить прогресс!</b>\n\n"
			"Не забудьте:\n"
			"• Взвеситься\n"
			"• Сделать фото прогресса\n"
			"• Обновить цели\n\n"
			"Это поможет отследить результаты и получить звезды!"
		)
		return await self._send_to_all_users(message, parse_mode="HTML")
	
	async def send_goal_reminder(self) -> int:
		"""Отправить напоминание о целях"""
		message = (
			"🎯 <b>Напомним о ваших целях</b>\n\n"
			"Регулярно проверяйте прогресс к цели в разделе 'Цели и прогресс'.\n"
			"Каждый шаг к цели — это победа!"
		)
		return await self._send_to_all_users(message, parse_mode="HTML")
	
	async def send_referral_reminder(self) -> int:
		"""Отправить напоминание о реферальной программе"""
		message = (
			"🔗 <b>Пригласите друзей!</b>\n\n"
			"За каждого друга вы получите 100 звезд!\n"
			"Друг получит скидку 10% на программу.\n\n"
			"Ваша реферальная ссылка в разделе 'Реферальная ссылка'."
		)
		return await self._send_to_all_users(message, parse_mode="HTML")
	
	async def send_monthly_raffle_reminder(self) -> int:
		"""Отправить напоминание о ежемесячном розыгрыше"""
		message = (
			"🏆 <b>Ежемесячный розыгрыш призов!</b>\n\n"
			"1-го числа месяца топ-5 пользователей по звездам получат призы!\n"
			"Тренируйтесь и зарабатывайте звезды!"
		)
		return await self._send_to_all_users(message, parse_mode="HTML")
	
	async def _send_to_all_users(self, message: str, parse_mode: Optional[str] = None) -> int:
		"""Отправить сообщение всем пользователям с уведомлениями"""
		async_session = get_session_maker()
		async with async_session() as session:
			users = (await session.execute(
				select(User.tg_user_id).where(User.notifications_enabled == True)
			)).scalars().all()
		
		sent_count = 0
		for user_id in users:
			try:
				await self.bot.send_message(user_id, message, parse_mode=parse_mode)
				sent_count += 1
				await asyncio.sleep(0.05)  # Небольшая задержка между отправками
			except Exception as e:
				print(f"Error sending message to user {user_id}: {e}")
				continue
		
		return sent_count
	
	async def send_to_specific_users(self, user_ids: List[int], message: str, parse_mode: Optional[str] = None) -> int:
		"""Отправить сообщение конкретным пользователям"""
		sent_count = 0
		for user_id in user_ids:
			try:
				await self.bot.send_message(user_id, message, parse_mode=parse_mode)
				sent_count += 1
				await asyncio.sleep(0.05)
			except Exception as e:
				print(f"Error sending message to user {user_id}: {e}")
				continue
		
		return sent_count
	
	async def send_to_users_by_level(self, level: str, message: str, parse_mode: Optional[str] = None) -> int:
		"""Отправить сообщение пользователям определенного уровня"""
		async_session = get_session_maker()
		async with async_session() as session:
			users = (await session.execute(
				select(User.tg_user_id).where(
					User.level == level,
					User.notifications_enabled == True
				)
			)).scalars().all()
		
		return await self.send_to_specific_users(list(users), message, parse_mode)
	
	async def send_to_new_users(self, days: int = 7, message: str = None, parse_mode: Optional[str] = None) -> int:
		"""Отправить сообщение новым пользователям"""
		if message is None:
			message = (
				"👋 <b>Добро пожаловать в FitCoach!</b>\n\n"
				"Мы рады, что вы присоединились к нам!\n"
				"Не забудьте:\n"
				"• Выбрать программу в /start\n"
				"• Настроить цели в личном кабинете\n"
				"• Начать первую тренировку\n\n"
				"Удачи на пути к результатам! 💪"
			)
		
		cutoff_date = datetime.utcnow() - timedelta(days=days)
		async_session = get_session_maker()
		async with async_session() as session:
			users = (await session.execute(
				select(User.tg_user_id).where(
					User.created_at >= cutoff_date,
					User.notifications_enabled == True
				)
			)).scalars().all()
		
		return await self.send_to_specific_users(list(users), message, parse_mode)
	
	async def send_to_inactive_users(self, days: int = 14, message: str = None, parse_mode: Optional[str] = None) -> int:
		"""Отправить сообщение неактивным пользователям"""
		if message is None:
			message = (
				"💪 <b>Мы скучаем по вам!</b>\n\n"
				"Не забудьте про тренировки и цели.\n"
				"Каждый день — это новая возможность стать лучше!\n\n"
				"Начните тренировку прямо сейчас: /workouts"
			)
		
		cutoff_date = datetime.utcnow() - timedelta(days=days)
		async_session = get_session_maker()
		async with async_session() as session:
			users = (await session.execute(
				select(User.tg_user_id).where(
					User.last_activity < cutoff_date,
					User.notifications_enabled == True
				)
			)).scalars().all()
		
		return await self.send_to_specific_users(list(users), message, parse_mode)


class ScheduledBroadcaster:
	"""Планировщик рассылок"""
	
	def __init__(self, bot: Bot):
		self.bot = bot
		self.broadcast_manager = BroadcastManager(bot)
	
	async def run_morning_broadcast(self):
		"""Утренняя рассылка (8:00)"""
		await self.broadcast_manager.send_motivational_message()
		await self.broadcast_manager.send_workout_reminder()
	
	async def run_afternoon_broadcast(self):
		"""Дневная рассылка (12:00)"""
		await self.broadcast_manager.send_nutrition_tip()
		await self.broadcast_manager.send_goal_reminder()
	
	async def run_evening_broadcast(self):
		"""Вечерняя рассылка (18:00)"""
		await self.broadcast_manager.send_workout_tip()
		await self.broadcast_manager.send_star_reminder()
	
	async def run_night_broadcast(self):
		"""Ночная рассылка (22:00)"""
		await self.broadcast_manager.send_weekly_progress_check()
	
	async def run_weekly_broadcast(self):
		"""Еженедельная рассылка (воскресенье 10:00)"""
		await self.broadcast_manager.send_referral_reminder()
		await self.broadcast_manager.send_monthly_raffle_reminder()
	
	async def run_monthly_broadcast(self):
		"""Ежемесячная рассылка (1-го числа)"""
		# Здесь должна быть логика розыгрыша призов
		message = (
			"🏆 <b>Результаты ежемесячного розыгрыша!</b>\n\n"
			"Победители будут объявлены в ближайшее время.\n"
			"Продолжайте тренироваться и зарабатывать звезды!"
		)
		await self.broadcast_manager._send_to_all_users(message, parse_mode="HTML")


class NotificationManager:
	"""Менеджер уведомлений"""
	
	def __init__(self, bot: Bot):
		self.bot = bot
	
	async def send_workout_completion_notification(self, user_id: int, workout_name: str):
		"""Уведомление о завершении тренировки"""
		message = f"✅ <b>Тренировка завершена!</b>\n\n{workout_name}\n\nОтличная работа! 💪"
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending workout completion notification to {user_id}: {e}")
	
	async def send_goal_achievement_notification(self, user_id: int, goal_name: str):
		"""Уведомление о достижении цели"""
		message = f"🎯 <b>Цель достигнута!</b>\n\n{goal_name}\n\nПоздравляем! Поставьте новую цель!"
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending goal achievement notification to {user_id}: {e}")
	
	async def send_star_earned_notification(self, user_id: int, stars: int, reason: str):
		"""Уведомление о получении звезд"""
		message = f"⭐ <b>Получено {stars} звезд!</b>\n\nПричина: {reason}\n\nНакопленные звезды можно обменять на призы!"
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending star earned notification to {user_id}: {e}")
	
	async def send_prize_redeemed_notification(self, user_id: int, prize_name: str):
		"""Уведомление об обмене приза"""
		message = f"🎁 <b>Приз обменян!</b>\n\n{prize_name}\n\nМы свяжемся с вами для доставки!"
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending prize redeemed notification to {user_id}: {e}")
	
	async def send_referral_bonus_notification(self, user_id: int, friend_name: str):
		"""Уведомление о реферальном бонусе"""
		message = f"🔗 <b>Реферальный бонус!</b>\n\nВаш друг {friend_name} присоединился!\n\nВы получили 100 звезд!"
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending referral bonus notification to {user_id}: {e}")
	
	async def send_payment_success_notification(self, user_id: int, program_name: str):
		"""Уведомление об успешной оплате"""
		message = f"✅ <b>Оплата прошла успешно!</b>\n\nПрограмма: {program_name}\n\nДоступ открыт! Начните тренировки: /workouts"
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending payment success notification to {user_id}: {e}")
	
	async def send_weekly_progress_summary(self, user_id: int, stats: Dict):
		"""Еженедельная сводка прогресса"""
		message = (
			f"📊 <b>Еженедельная сводка</b>\n\n"
			f"Тренировок: {stats.get('workouts', 0)}\n"
			f"Приемов пищи: {stats.get('meals', 0)}\n"
			f"Звезд заработано: {stats.get('stars_earned', 0)}\n"
			f"Прогресс к цели: {stats.get('goal_progress', 0)}%\n\n"
			f"Продолжайте в том же духе! 💪"
		)
		try:
			await self.bot.send_message(user_id, message, parse_mode="HTML")
		except Exception as e:
			print(f"Error sending weekly progress summary to {user_id}: {e}")