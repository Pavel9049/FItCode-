#!/usr/bin/env python3
"""
Скрипт для проверки базы данных
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_session_maker
from sqlalchemy import text

async def check_database():
    """Проверить базу данных"""
    print("🔍 Проверка базы данных...")
    
    async_session = get_session_maker()
    errors = []
    
    try:
        async with async_session() as session:
            # Проверяем все таблицы
            tables_to_check = [
                'users', 'programs', 'exercises', 'meals', 'purchases',
                'workout_plans', 'meal_plans', 'star_events', 'referrals',
                'prize_redemptions', 'goals', 'progress_photos', 'prizes'
            ]
            
            for table in tables_to_check:
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"✅ {table}: {count} записей")
                except Exception as e:
                    error_msg = f"❌ {table}: {e}"
                    print(error_msg)
                    errors.append(error_msg)
            
            # Проверяем структуру таблицы users
            try:
                result = await session.execute(text("PRAGMA table_info(users)"))
                columns = result.fetchall()
                required_columns = [
                    'id', 'tg_user_id', 'first_name', 'last_name', 'username',
                    'level', 'has_pro_support', 'height_cm', 'weight_kg', 'gender',
                    'age', 'notifications_enabled', 'stars', 'created_at'
                ]
                
                existing_columns = [col[1] for col in columns]
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                if missing_columns:
                    error_msg = f"❌ users: отсутствуют колонки {missing_columns}"
                    print(error_msg)
                    errors.append(error_msg)
                else:
                    print("✅ users: все необходимые колонки присутствуют")
                    
            except Exception as e:
                error_msg = f"❌ users structure: {e}"
                print(error_msg)
                errors.append(error_msg)
            
            # Проверяем структуру таблицы meals
            try:
                result = await session.execute(text("PRAGMA table_info(meals)"))
                columns = result.fetchall()
                required_columns = [
                    'id', 'title', 'photo_url', 'kcal', 'proteins', 'fats', 'carbs',
                    'recipe', 'article_url', 'tags'
                ]
                
                existing_columns = [col[1] for col in columns]
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                if missing_columns:
                    error_msg = f"❌ meals: отсутствуют колонки {missing_columns}"
                    print(error_msg)
                    errors.append(error_msg)
                else:
                    print("✅ meals: все необходимые колонки присутствуют")
                    
            except Exception as e:
                error_msg = f"❌ meals structure: {e}"
                print(error_msg)
                errors.append(error_msg)
    
    except Exception as e:
        error_msg = f"❌ Database connection: {e}"
        print(error_msg)
        errors.append(error_msg)
    
    print(f"\n📊 Результаты проверки БД:")
    print(f"  ❌ Ошибок: {len(errors)}")
    
    if errors:
        print(f"\n❌ Ошибки базы данных:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ База данных в порядке")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)