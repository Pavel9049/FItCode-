from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, Purchase, Program, Referral, StarEvent, Goal, ProgressPhoto
from app.db.session import get_session_maker
from app.db.models import ProgramLevel
from datetime import datetime, timedelta


async def get_user_by_tg_id(tg_user_id: int) -> Optional[User]:
	"""Получить пользователя по Telegram ID"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		return user


async def create_user_if_not_exists(
	tg_user_id: int,
	first_name: Optional[str] = None,
	last_name: Optional[str] = None,
	username: Optional[str] = None
) -> User:
	"""Создать пользователя, если он не существует"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			user = User(
				tg_user_id=tg_user_id,
				first_name=first_name,
				last_name=last_name,
				username=username
			)
			session.add(user)
			await session.commit()
			await session.refresh(user)
		
		return user


async def user_has_paid_access(tg_user_id: int) -> bool:
	"""Проверить, есть ли у пользователя оплаченный доступ"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return False
		
		purchase = (await session.execute(
			select(Purchase).where(Purchase.user_id == user.id, Purchase.paid == True)
		)).scalar_one_or_none()
		
		return bool(purchase)


async def get_user_level(tg_user_id: int) -> Optional[ProgramLevel]:
	"""Получить уровень программы пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		return user.level if user else None


async def update_user_level(tg_user_id: int, level: ProgramLevel) -> bool:
	"""Обновить уровень программы пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		result = await session.execute(
			update(User)
			.where(User.tg_user_id == tg_user_id)
			.values(level=level)
		)
		await session.commit()
		return result.rowcount > 0


async def get_user_referral_discount(tg_user_id: int) -> int:
	"""Получить реферальную скидку пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return 0
		
		referral = (await session.execute(
			select(Referral).where(Referral.referred_user_id == user.id)
		)).scalar_one_or_none()
		
		return referral.discount_percent if referral else 0


async def add_stars_to_user(tg_user_id: int, stars: int, reason: str) -> bool:
	"""Добавить звезды пользователю"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return False
		
		# Обновляем количество звезд
		user.stars += stars
		
		# Создаем запись о событии
		star_event = StarEvent(
			user_id=user.id,
			reason=reason,
			stars_delta=stars
		)
		session.add(star_event)
		
		await session.commit()
		return True


async def get_user_stars(tg_user_id: int) -> int:
	"""Получить количество звезд пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		return user.stars if user else 0


async def create_user_goal(
	tg_user_id: int,
	goal_type: str,
	target_weight: Optional[float] = None,
	deadline: Optional[datetime] = None,
	start_weight: Optional[float] = None
) -> Optional[Goal]:
	"""Создать цель пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return None
		
		goal = Goal(
			user_id=user.id,
			goal_type=goal_type,
			target_weight_kg=target_weight,
			deadline=deadline,
			start_weight_kg=start_weight or user.weight_kg
		)
		session.add(goal)
		await session.commit()
		await session.refresh(goal)
		
		return goal


async def get_user_goals(tg_user_id: int) -> List[Goal]:
	"""Получить цели пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return []
		
		goals = (await session.execute(
			select(Goal).where(Goal.user_id == user.id).order_by(Goal.created_at.desc())
		)).scalars().all()
		
		return list(goals)


async def save_progress_photo(
	tg_user_id: int,
	photo_file_id: str,
	weight: Optional[float] = None,
	view: Optional[str] = None
) -> Optional[ProgressPhoto]:
	"""Сохранить фото прогресса"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return None
		
		progress_photo = ProgressPhoto(
			user_id=user.id,
			photo_file_id=photo_file_id,
			weight_kg=weight,
			view=view
		)
		session.add(progress_photo)
		await session.commit()
		await session.refresh(progress_photo)
		
		return progress_photo


async def get_user_progress_photos(tg_user_id: int, limit: int = 10) -> List[ProgressPhoto]:
	"""Получить фото прогресса пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return []
		
		photos = (await session.execute(
			select(ProgressPhoto)
			.where(ProgressPhoto.user_id == user.id)
			.order_by(ProgressPhoto.created_at.desc())
			.limit(limit)
		)).scalars().all()
		
		return list(photos)


async def update_user_profile(
	tg_user_id: int,
	height_cm: Optional[int] = None,
	weight_kg: Optional[float] = None,
	gender: Optional[str] = None,
	age: Optional[int] = None
) -> bool:
	"""Обновить профиль пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		update_data = {}
		if height_cm is not None:
			update_data['height_cm'] = height_cm
		if weight_kg is not None:
			update_data['weight_kg'] = weight_kg
		if gender is not None:
			update_data['gender'] = gender
		if age is not None:
			update_data['age'] = age
		
		if not update_data:
			return False
		
		result = await session.execute(
			update(User)
			.where(User.tg_user_id == tg_user_id)
			.values(**update_data)
		)
		await session.commit()
		return result.rowcount > 0


async def toggle_user_notifications(tg_user_id: int) -> bool:
	"""Переключить уведомления пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return False
		
		user.notifications_enabled = not user.notifications_enabled
		await session.commit()
		return user.notifications_enabled


async def get_users_with_notifications() -> List[int]:
	"""Получить список пользователей с включенными уведомлениями"""
	async_session = get_session_maker()
	async with async_session() as session:
		users = (await session.execute(
			select(User.tg_user_id).where(User.notifications_enabled == True)
		)).scalars().all()
		
		return list(users)


async def get_referral_stats(tg_user_id: int) -> Dict[str, Any]:
	"""Получить статистику рефералов пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return {"total_referrals": 0, "active_referrals": 0, "total_bonus": 0}
		
		# Общее количество рефералов
		total_referrals = (await session.execute(
			select(Referral).where(Referral.referrer_user_id == user.id)
		)).scalars().all()
		
		# Активные рефералы (с оплаченными покупками)
		active_referrals = []
		for referral in total_referrals:
			if referral.referred_user_id:
				referred_user = (await session.execute(
					select(User).where(User.id == referral.referred_user_id)
				)).scalar_one_or_none()
				
				if referred_user:
					purchase = (await session.execute(
						select(Purchase).where(Purchase.user_id == referred_user.id, Purchase.paid == True)
					)).scalar_one_or_none()
					
					if purchase:
						active_referrals.append(referral)
		
		# Общий бонус (100 звезд за каждого активного реферала)
		total_bonus = len(active_referrals) * 100
		
		return {
			"total_referrals": len(total_referrals),
			"active_referrals": len(active_referrals),
			"total_bonus": total_bonus
		}


async def get_user_workout_stats(tg_user_id: int, days: int = 30) -> Dict[str, Any]:
	"""Получить статистику тренировок пользователя"""
	# В реальном проекте здесь должна быть логика подсчета тренировок
	# Пока что возвращаем заглушку
	return {
		"total_workouts": 0,
		"workouts_this_week": 0,
		"streak_days": 0,
		"favorite_exercise": "Не определено"
	}


async def get_user_nutrition_stats(tg_user_id: int, days: int = 30) -> Dict[str, Any]:
	"""Получить статистику питания пользователя"""
	# В реальном проекте здесь должна быть логика подсчета питания
	# Пока что возвращаем заглушку
	return {
		"total_meals": 0,
		"avg_calories": 0,
		"avg_proteins": 0,
		"avg_fats": 0,
		"avg_carbs": 0
	}


async def get_user_progress_stats(tg_user_id: int) -> Dict[str, Any]:
	"""Получить статистику прогресса пользователя"""
	async_session = get_session_maker()
	async with async_session() as session:
		user = (await session.execute(
			select(User).where(User.tg_user_id == tg_user_id)
		)).scalar_one_or_none()
		
		if not user:
			return {"weight_change": 0, "goal_progress": 0, "photos_count": 0}
		
		# Изменение веса
		weight_change = 0
		if user.weight_kg:
			# Получаем начальный вес из цели
			goal = (await session.execute(
				select(Goal).where(Goal.user_id == user.id).order_by(Goal.created_at.desc())
			)).scalar_one_or_none()
			
			if goal and goal.start_weight_kg:
				weight_change = user.weight_kg - goal.start_weight_kg
		
		# Прогресс к цели
		goal_progress = 0
		if goal and goal.target_weight_kg and goal.start_weight_kg:
			if goal.goal_type == "lose_weight":
				total_to_lose = goal.start_weight_kg - goal.target_weight_kg
				current_lost = goal.start_weight_kg - user.weight_kg
				if total_to_lose > 0:
					goal_progress = min(100, max(0, (current_lost / total_to_lose) * 100))
			elif goal.goal_type == "gain_mass":
				total_to_gain = goal.target_weight_kg - goal.start_weight_kg
				current_gained = user.weight_kg - goal.start_weight_kg
				if total_to_gain > 0:
					goal_progress = min(100, max(0, (current_gained / total_to_gain) * 100))
		
		# Количество фото прогресса
		photos_count = (await session.execute(
			select(ProgressPhoto).where(ProgressPhoto.user_id == user.id)
		)).scalars().all()
		
		return {
			"weight_change": round(weight_change, 1),
			"goal_progress": round(goal_progress, 1),
			"photos_count": len(photos_count)
		}