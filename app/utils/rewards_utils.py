from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random
from app.db.models import Prize, StarEvent, User
from app.db.session import get_session_maker
from sqlalchemy import select, update


class RewardsManager:
	"""Менеджер системы наград"""
	
	def __init__(self):
		self.prizes = self._load_default_prizes()
	
	def _load_default_prizes(self) -> List[Dict]:
		"""Загрузить стандартные призы"""
		return [
			{
				'title': 'Беспроводные наушники',
				'stars_required': 500,
				'description': 'Качественные беспроводные наушники для тренировок',
				'category': 'electronics'
			},
			{
				'title': 'Умные часы',
				'stars_required': 800,
				'description': 'Умные часы для отслеживания тренировок',
				'category': 'electronics'
			},
			{
				'title': 'Кроссовки для фитнеса',
				'stars_required': 700,
				'description': 'Профессиональные кроссовки для тренировок',
				'category': 'sport'
			},
			{
				'title': '2990 ₽ на карту',
				'stars_required': 400,
				'description': 'Денежный приз на любую карту',
				'category': 'money'
			},
			{
				'title': 'Протеиновый порошок',
				'stars_required': 200,
				'description': 'Качественный протеин для восстановления',
				'category': 'nutrition'
			},
			{
				'title': 'Фитнес-резинки',
				'stars_required': 150,
				'description': 'Набор резинок для домашних тренировок',
				'category': 'sport'
			},
			{
				'title': 'Скакалка',
				'stars_required': 100,
				'description': 'Профессиональная скакалка для кардио',
				'category': 'sport'
			},
			{
				'title': 'Бутылка для воды',
				'stars_required': 80,
				'description': 'Спортивная бутылка для воды',
				'category': 'sport'
			}
		]
	
	async def get_available_prizes(self) -> List[Dict]:
		"""Получить доступные призы"""
		async_session = get_session_maker()
		async with async_session() as session:
			prizes = (await session.execute(
				select(Prize).where(Prize.is_active == True).order_by(Prize.stars_required)
			)).scalars().all()
			
			if not prizes:
				# Если призов нет в БД, возвращаем стандартные
				return self.prizes
			
			return [
				{
					'title': prize.title,
					'stars_required': prize.stars_required,
					'description': f'Приз за {prize.stars_required} звезд',
					'category': 'custom'
				}
				for prize in prizes
			]
	
	async def can_redeem_prize(self, user_id: int, prize_stars: int) -> bool:
		"""Проверить, может ли пользователь обменять приз"""
		async_session = get_session_maker()
		async with async_session() as session:
			user = (await session.execute(
				select(User).where(User.id == user_id)
			)).scalar_one_or_none()
			
			return user and user.stars >= prize_stars
	
	async def redeem_prize(self, user_id: int, prize_title: str, prize_stars: int) -> bool:
		"""Обменять приз на звезды"""
		async_session = get_session_maker()
		async with async_session() as session:
			user = (await session.execute(
				select(User).where(User.id == user_id)
			)).scalar_one_or_none()
			
			if not user or user.stars < prize_stars:
				return False
			
			# Списываем звезды
			user.stars -= prize_stars
			
			# Создаем запись о событии
			star_event = StarEvent(
				user_id=user_id,
				reason=f"Обмен приза: {prize_title}",
				stars_delta=-prize_stars
			)
			session.add(star_event)
			
			await session.commit()
			return True


class MotivationManager:
	"""Менеджер мотивации"""
	
	def __init__(self):
		self.motivational_quotes = self._load_motivational_quotes()
		self.workout_tips = self._load_workout_tips()
		self.nutrition_tips = self._load_nutrition_tips()
	
	def _load_motivational_quotes(self) -> List[str]:
		"""Загрузить мотивационные цитаты"""
		return [
			"💪 Каждая тренировка — это шаг к лучшей версии себя",
			"🔥 Сила не в том, сколько ты можешь поднять, а в том, сколько раз ты можешь подняться",
			"🏃‍♂️ Прогресс — это не всегда быстро, но он всегда постоянен",
			"⭐ Сегодняшние усилия — это завтрашние результаты",
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
	
	def _load_workout_tips(self) -> List[str]:
		"""Загрузить советы по тренировкам"""
		return [
			"💡 Совет: Всегда начинайте тренировку с разминки — это защитит от травм",
			"💡 Совет: Сфокусируйтесь на технике выполнения, а не на весе",
			"💡 Совет: Не забывайте про растяжку после тренировки",
			"💡 Совет: Пейте воду во время тренировки",
			"💡 Совет: Давайте мышцам время на восстановление",
			"💡 Совет: Ведите дневник тренировок для отслеживания прогресса",
			"💡 Совет: Меняйте программу тренировок каждые 4-6 недель",
			"💡 Совет: Не пропускайте тренировки ног — они важны для всего тела",
			"💡 Совет: Кардио после силовой тренировки сжигает больше жира",
			"💡 Совет: Слушайте свое тело — отдых так же важен, как и тренировки"
		]
	
	def _load_nutrition_tips(self) -> List[str]:
		"""Загрузить советы по питанию"""
		return [
			"🍎 Совет: Ешьте белок с каждым приемом пищи для роста мышц",
			"🥗 Совет: Овощи должны занимать половину тарелки",
			"💧 Совет: Пейте 2-3 литра воды в день",
			"🥜 Совет: Не бойтесь полезных жиров — они важны для гормонов",
			"🍚 Совет: Сложные углеводы дают энергию для тренировок",
			"🥛 Совет: Творог перед сном — отличный источник казеина",
			"🥑 Совет: Авокадо содержит полезные жиры и клетчатку",
			"🐟 Совет: Рыба 2-3 раза в неделю для омега-3",
			"🥜 Совет: Орехи — отличный перекус, но следите за порцией",
			"🍌 Совет: Банан после тренировки восстанавливает гликоген"
		]
	
	def get_random_quote(self) -> str:
		"""Получить случайную мотивационную цитату"""
		return random.choice(self.motivational_quotes)
	
	def get_random_workout_tip(self) -> str:
		"""Получить случайный совет по тренировкам"""
		return random.choice(self.workout_tips)
	
	def get_random_nutrition_tip(self) -> str:
		"""Получить случайный совет по питанию"""
		return random.choice(self.nutrition_tips)
	
	def get_daily_motivation(self) -> str:
		"""Получить ежедневную мотивацию"""
		quote = self.get_random_quote()
		tip = self.get_random_workout_tip()
		
		return f"{quote}\n\n{tip}"
	
	def get_workout_reminder(self) -> str:
		"""Получить напоминание о тренировке"""
		reminders = [
			"🏋️‍♂️ Время тренировки! Выполни тренировку — получи звезду!",
			"💪 Не забудь про тренировку сегодня! Твой прогресс ждет!",
			"🔥 Готов к тренировке? Каждая тренировка приближает к цели!",
			"⭐ Сегодня отличный день для тренировки! Начни прямо сейчас!",
			"🎯 Тренировка — это инвестиция в себя! Не пропускай!"
		]
		return random.choice(reminders)


class ProgressTracker:
	"""Трекер прогресса"""
	
	@staticmethod
	async def calculate_progress_score(user_id: int) -> int:
		"""
		Рассчитать оценку прогресса пользователя (1-5 звезд)
		
		Args:
			user_id: ID пользователя
		
		Returns:
			int: Количество звезд (1-5)
		"""
		async_session = get_session_maker()
		async with async_session() as session:
			user = (await session.execute(
				select(User).where(User.id == user_id)
			)).scalar_one_or_none()
			
			if not user:
				return 0
			
			score = 0
			
			# Проверяем изменение веса
			if user.weight_kg:
				# Получаем начальный вес из цели
				from app.db.models import Goal
				goal = (await session.execute(
					select(Goal).where(Goal.user_id == user.id).order_by(Goal.created_at.desc())
				)).scalar_one_or_none()
				
				if goal and goal.start_weight_kg:
					weight_change = abs(user.weight_kg - goal.start_weight_kg)
					if weight_change >= 5:
						score += 2
					elif weight_change >= 2:
						score += 1
			
			# Проверяем количество тренировок (заглушка)
			# В реальном проекте нужно считать реальные тренировки
			workout_count = 0  # Здесь должна быть логика подсчета
			if workout_count >= 7:
				score += 2
			elif workout_count >= 4:
				score += 1
			
			# Проверяем количество фото прогресса
			from app.db.models import ProgressPhoto
			photos = (await session.execute(
				select(ProgressPhoto).where(ProgressPhoto.user_id == user.id)
			)).scalars().all()
			
			if len(photos) >= 3:
				score += 1
			
			return min(5, max(1, score))
	
	@staticmethod
	async def award_stars_for_progress(user_id: int, reason: str) -> int:
		"""
		Наградить звездами за прогресс
		
		Args:
			user_id: ID пользователя
			reason: Причина награды
		
		Returns:
			int: Количество награжденных звезд
		"""
		stars = await ProgressTracker.calculate_progress_score(user_id)
		
		if stars > 0:
			async_session = get_session_maker()
			async with async_session() as session:
				user = (await session.execute(
					select(User).where(User.id == user_id)
				)).scalar_one_or_none()
				
				if user:
					user.stars += stars
					
					star_event = StarEvent(
						user_id=user_id,
						reason=reason,
						stars_delta=stars
					)
					session.add(star_event)
					
					await session.commit()
		
		return stars
	
	@staticmethod
	async def award_stars_for_workout_streak(user_id: int, streak_days: int) -> int:
		"""
		Наградить звездами за серию тренировок
		
		Args:
			user_id: ID пользователя
			streak_days: Количество дней подряд
		
		Returns:
			int: Количество награжденных звезд
		"""
		if streak_days >= 7:
			stars = 3
		elif streak_days >= 5:
			stars = 2
		elif streak_days >= 3:
			stars = 1
		else:
			stars = 0
		
		if stars > 0:
			async_session = get_session_maker()
			async with async_session() as session:
				user = (await session.execute(
					select(User).where(User.id == user_id)
				)).scalar_one_or_none()
				
				if user:
					user.stars += stars
					
					star_event = StarEvent(
						user_id=user_id,
						reason=f"Серия тренировок: {streak_days} дней",
						stars_delta=stars
					)
					session.add(star_event)
					
					await session.commit()
		
		return stars
	
	@staticmethod
	async def award_stars_for_meal_completion(user_id: int, meals_count: int) -> int:
		"""
		Наградить звездами за соблюдение питания
		
		Args:
			user_id: ID пользователя
			meals_count: Количество соблюденных приемов пищи
		
		Returns:
			int: Количество награжденных звезд
		"""
		if meals_count >= 5:
			stars = 2
		elif meals_count >= 3:
			stars = 1
		else:
			stars = 0
		
		if stars > 0:
			async_session = get_session_maker()
			async with async_session() as session:
				user = (await session.execute(
					select(User).where(User.id == user_id)
				)).scalar_one_or_none()
				
				if user:
					user.stars += stars
					
					star_event = StarEvent(
						user_id=user_id,
						reason=f"Соблюдение питания: {meals_count} приемов",
						stars_delta=stars
					)
					session.add(star_event)
					
					await session.commit()
		
		return stars


# Глобальные экземпляры
rewards_manager = RewardsManager()
motivation_manager = MotivationManager()
progress_tracker = ProgressTracker()