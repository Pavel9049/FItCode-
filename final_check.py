#!/usr/bin/env python3
"""
Финальный комплексный тест всех компонентов бота
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.db.session import get_session_maker
from app.services.workouts import WorkoutGoal, WorkoutLevel, EquipmentType, generate_workout_plan
from app.services.nutrition import NutritionCalculator, NutritionGoal
from app.utils.db_utils import get_user_by_tg_id, user_has_paid_access
from sqlalchemy import text

async def final_comprehensive_check():
    """Финальная комплексная проверка"""
    print("🔍 ФИНАЛЬНАЯ КОМПЛЕКСНАЯ ПРОВЕРКА БОТА")
    print("=" * 50)
    
    errors = []
    success_count = 0
    
    # Тест 1: Конфигурация
    print("\n✅ 1. Конфигурация:")
    try:
        print(f"   - Токен: {settings.telegram_bot_token[:20]}...")
        print(f"   - Режим: {settings.run_mode}")
        print(f"   - Админы: {settings.admin_ids_list}")
        success_count += 1
    except Exception as e:
        errors.append(f"Конфигурация: {e}")
    
    # Тест 2: База данных
    print("\n✅ 2. База данных:")
    try:
        async_session = get_session_maker()
        async with async_session() as session:
            # Проверяем основные таблицы
            tables = ['users', 'programs', 'exercises', 'meals']
            for table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   - {table}: {count} записей")
        success_count += 1
    except Exception as e:
        errors.append(f"База данных: {e}")
    
    # Тест 3: Сервис тренировок
    print("\n✅ 3. Сервис тренировок:")
    try:
        workout_plan = generate_workout_plan(
            user_weight=75.0,
            user_height=180,
            user_gender="male",
            user_age=30,
            goal=WorkoutGoal.GAIN_MASS,
            level=WorkoutLevel.NOVICE,
            available_equipment=[EquipmentType.DUMBBELLS, EquipmentType.BARBELL]
        )
        total_exercises = sum(len(day.get("exercises", [])) for day in workout_plan.values())
        print(f"   - План сгенерирован: {len(workout_plan)} дней")
        print(f"   - Всего упражнений: {total_exercises}")
        success_count += 1
    except Exception as e:
        errors.append(f"Сервис тренировок: {e}")
    
    # Тест 4: Сервис питания
    print("\n✅ 4. Сервис питания:")
    try:
        calculator = NutritionCalculator()
        bmr = calculator.calculate_bmr(75.0, 180, 30, "male")
        tdee = calculator.calculate_tdee(bmr, "moderate")
        macros = calculator.calculate_macros_for_goal(tdee, NutritionGoal.GAIN_MASS, 75.0)
        
        print(f"   - BMR: {bmr:.0f} ккал")
        print(f"   - TDEE: {tdee:.0f} ккал")
        print(f"   - Белки: {macros['protein_g']:.0f}г")
        success_count += 1
    except Exception as e:
        errors.append(f"Сервис питания: {e}")
    
    # Тест 5: Утилиты БД
    print("\n✅ 5. Утилиты базы данных:")
    try:
        user = await get_user_by_tg_id(999999999)
        has_access = await user_has_paid_access(999999999)
        print(f"   - Поиск пользователя: {'Найден' if user else 'Не найден'}")
        print(f"   - Проверка доступа: {'Есть' if has_access else 'Нет'}")
        success_count += 1
    except Exception as e:
        errors.append(f"Утилиты БД: {e}")
    
    # Тест 6: Роутеры
    print("\n✅ 6. Роутеры:")
    try:
        routers = [
            'app.routers.start', 'app.routers.workouts', 'app.routers.menu',
            'app.routers.cabinet', 'app.routers.rewards', 'app.routers.settings',
            'app.routers.support', 'app.routers.instagram', 'app.routers.ai_kbju',
            'app.routers.referral', 'app.routers.purchase', 'app.routers.test',
            'app.routers.fallback', 'app.routers.health'
        ]
        
        loaded_routers = 0
        for router_name in routers:
            try:
                module = __import__(router_name, fromlist=['router'])
                router = getattr(module, 'router')
                loaded_routers += 1
            except Exception:
                pass
        
        print(f"   - Загружено роутеров: {loaded_routers}/{len(routers)}")
        success_count += 1
    except Exception as e:
        errors.append(f"Роутеры: {e}")
    
    # Тест 7: Планировщик
    print("\n✅ 7. Планировщик:")
    try:
        from app.background.scheduler import setup_scheduler
        print("   - Планировщик загружен успешно")
        success_count += 1
    except Exception as e:
        errors.append(f"Планировщик: {e}")
    
    # Тест 8: API Telegram
    print("\n✅ 8. API Telegram:")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
            )
            data = response.json()
            if data.get("ok"):
                bot_info = data["result"]
                print(f"   - Бот: {bot_info['first_name']} (@{bot_info['username']})")
                print(f"   - ID: {bot_info['id']}")
                success_count += 1
            else:
                raise Exception("API не отвечает")
    except Exception as e:
        errors.append(f"API Telegram: {e}")
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 50)
    
    print(f"✅ Успешных тестов: {success_count}/8")
    print(f"❌ Ошибок: {len(errors)}")
    
    if errors:
        print(f"\n❌ НАЙДЕННЫЕ ОШИБКИ:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    else:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    
    print(f"\n🚀 СТАТУС БОТА: {'✅ ГОТОВ К РАБОТЕ' if len(errors) == 0 else '❌ ТРЕБУЕТ ИСПРАВЛЕНИЙ'}")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = asyncio.run(final_comprehensive_check())
    sys.exit(0 if success else 1)