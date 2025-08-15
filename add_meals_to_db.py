#!/usr/bin/env python3
"""
Скрипт для добавления блюд в базу данных
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_session_maker
from app.db.models import Meal
from app.services.nutrition import MEALS_DATABASE
from sqlalchemy import text


async def add_meals_to_db():
    """Добавить блюда в базу данных"""
    async_session = get_session_maker()
    
    async with async_session() as session:
        # Получаем все существующие блюда
        existing_meals = await session.execute(
            text("SELECT title FROM meals")
        )
        existing = {row[0] for row in existing_meals.fetchall()}
        
        added_count = 0
        
        # Добавляем блюда из MEALS_DATABASE
        for meal_type, meals in MEALS_DATABASE.items():
            for meal in meals:
                # Проверяем, не существует ли уже такое блюдо
                if meal.name not in existing:
                    db_meal = Meal(
                        title=meal.name,
                        photo_url=meal.image_url,
                        kcal=meal.calories,
                        proteins=meal.protein,
                        fats=meal.fat,
                        carbs=meal.carbs,
                        recipe=meal.recipe,
                        ingredients=", ".join(meal.ingredients),
                        cooking_time=meal.cooking_time,
                        difficulty=meal.difficulty,
                        tags=", ".join(meal.tags),
                        nutrition_notes=meal.nutrition_notes
                    )
                    session.add(db_meal)
                    added_count += 1
                    print(f"✅ Добавлено: {meal.name} ({meal_type.value})")
        
        await session.commit()
        print(f"\n🎉 Добавлено {added_count} новых блюд в базу данных!")


if __name__ == "__main__":
    asyncio.run(add_meals_to_db())