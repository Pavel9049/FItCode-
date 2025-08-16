#!/usr/bin/env python3
"""
Скрипт для добавления упражнений в базу данных
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_session_maker
from app.db.models import Exercise, ProgramLevel
from app.services.workouts import EXERCISES_DATABASE
from sqlalchemy import text


async def add_exercises_to_db():
    """Добавить упражнения в базу данных"""
    async_session = get_session_maker()
    
    async with async_session() as session:
        # Получаем все существующие упражнения
        existing_exercises = await session.execute(
            text("SELECT name, level FROM exercises")
        )
        existing = {(row[0], row[1]) for row in existing_exercises.fetchall()}
        
        added_count = 0
        
        # Добавляем упражнения из EXERCISES_DATABASE
        for muscle_group, levels in EXERCISES_DATABASE.items():
            for level, exercises in levels.items():
                for exercise in exercises:
                    # Проверяем, не существует ли уже такое упражнение
                    if (exercise.name, level.value) not in existing:
                        db_exercise = Exercise(
                            name=exercise.name,
                            muscle_group=exercise.muscle_group,
                            level=ProgramLevel(level.value),
                            requires_equipment=exercise.equipment.value != "bodyweight",
                            video_url=exercise.video_url,
                            description=exercise.description
                        )
                        session.add(db_exercise)
                        added_count += 1
                        print(f"✅ Добавлено: {exercise.name} ({muscle_group}, {level.value})")
        
        await session.commit()
        print(f"\n🎉 Добавлено {added_count} новых упражнений в базу данных!")


if __name__ == "__main__":
    asyncio.run(add_exercises_to_db())