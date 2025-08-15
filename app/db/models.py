from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger, ForeignKey, Boolean, DateTime, Text, Enum, Float, UniqueConstraint
from datetime import datetime, date
from typing import Optional
from app.db.session import Base
import enum


class ProgramLevel(str, enum.Enum):
	beginner = "beginner"      # Начинающий
	novice = "novice"          # Новичок
	advanced = "advanced"      # Продвинутый
	pro = "pro"                # Профессионал


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
	first_name: Mapped[Optional[str]] = mapped_column(String(128))
	last_name: Mapped[Optional[str]] = mapped_column(String(128))
	username: Mapped[Optional[str]] = mapped_column(String(128), index=True)

	level: Mapped[Optional[ProgramLevel]] = mapped_column(Enum(ProgramLevel), nullable=True)
	has_pro_support: Mapped[bool] = mapped_column(Boolean, default=False)

	height_cm: Mapped[Optional[int]] = mapped_column(Integer)
	weight_kg: Mapped[Optional[float]] = mapped_column(Float)
	gender: Mapped[Optional[str]] = mapped_column(String(16))
	age: Mapped[Optional[int]] = mapped_column(Integer)

	notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
	stars: Mapped[int] = mapped_column(Integer, default=0)

	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	purchases: Mapped[list["Purchase"]] = relationship(back_populates="user")


class Program(Base):
	__tablename__ = "programs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
	title: Mapped[str] = mapped_column(String(128))
	price_rub: Mapped[int] = mapped_column(Integer)
	description: Mapped[str] = mapped_column(Text)


class Purchase(Base):
	__tablename__ = "purchases"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
	gateway: Mapped[str] = mapped_column(String(32))  # stripe|yookassa|stars|crypto
	external_id: Mapped[str] = mapped_column(String(128), index=True)
	amount_rub: Mapped[int] = mapped_column(Integer)
	currency: Mapped[str] = mapped_column(String(8), default="RUB")
	paid: Mapped[bool] = mapped_column(Boolean, default=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	user: Mapped[User] = relationship(back_populates="purchases")


class Exercise(Base):
	__tablename__ = "exercises"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(128))
	muscle_group: Mapped[str] = mapped_column(String(32))  # back,biceps,triceps,shoulders,legs,forearms,abs
	level: Mapped[ProgramLevel] = mapped_column(Enum(ProgramLevel))
	requires_equipment: Mapped[bool] = mapped_column(Boolean, default=False)
	video_url: Mapped[Optional[str]] = mapped_column(String(512))
	description: Mapped[Optional[str]] = mapped_column(Text)

	__table_args__ = (
		UniqueConstraint("name", "level", name="uq_ex_name_level"),
	)


class WorkoutPlan(Base):
	__tablename__ = "workout_plans"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	week_start: Mapped[datetime] = mapped_column(DateTime, index=True)
	data_json: Mapped[str] = mapped_column(Text)  # сериализованный план на неделю


class Meal(Base):
	__tablename__ = "meals"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	title: Mapped[str] = mapped_column(String(256))
	photo_url: Mapped[Optional[str]] = mapped_column(String(512))
	kcal: Mapped[int] = mapped_column(Integer)
	proteins: Mapped[float] = mapped_column(Float)
	fats: Mapped[float] = mapped_column(Float)
	carbs: Mapped[float] = mapped_column(Float)
	recipe: Mapped[str] = mapped_column(Text)
	article_url: Mapped[Optional[str]] = mapped_column(String(512))
	tags: Mapped[Optional[str]] = mapped_column(String(128))  # breakfast,lunch,dinner,snack


class MealPlan(Base):
	__tablename__ = "meal_plans"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	week_start: Mapped[datetime] = mapped_column(DateTime, index=True)
	data_json: Mapped[str] = mapped_column(Text)


class StarEvent(Base):
	__tablename__ = "star_events"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	reason: Mapped[str] = mapped_column(String(64))
	stars_delta: Mapped[int] = mapped_column(Integer)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Referral(Base):
	__tablename__ = "referrals"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	referrer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	referral_code: Mapped[str] = mapped_column(String(64), unique=True)
	referred_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
	discount_percent: Mapped[int] = mapped_column(Integer, default=10)
	bonus_awarded: Mapped[bool] = mapped_column(Boolean, default=False)


class Prize(Base):
	__tablename__ = "prizes"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	title: Mapped[str] = mapped_column(String(256))
	stars_required: Mapped[int] = mapped_column(Integer)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PrizeRedemption(Base):
	__tablename__ = "prize_redemptions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	prize_id: Mapped[int] = mapped_column(ForeignKey("prizes.id"))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GoalType(str, enum.Enum):
	lose_weight = "lose_weight"
	gain_mass = "gain_mass"
	cut = "cut"
	tone = "tone"


class Goal(Base):
	__tablename__ = "goals"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	goal_type: Mapped[str] = mapped_column(String(32))
	target_weight_kg: Mapped[Optional[float]] = mapped_column(Float)
	deadline: Mapped[Optional[date]] = mapped_column(DateTime)
	start_weight_kg: Mapped[Optional[float]] = mapped_column(Float)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProgressPhoto(Base):
	__tablename__ = "progress_photos"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	photo_file_id: Mapped[str] = mapped_column(String(256))
	weight_kg: Mapped[Optional[float]] = mapped_column(Float)
	view: Mapped[Optional[str]] = mapped_column(String(16))  # front/side/back
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)