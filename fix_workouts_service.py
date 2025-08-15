#!/usr/bin/env python3
"""
Скрипт для исправления сервиса тренировок
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.workouts import (
    WorkoutGoal, WorkoutLevel, EquipmentType, Exercise, WorkoutCalculator,
    EXERCISES_DATABASE, generate_workout_plan, get_exercises_for_muscle_group,
    get_muscle_groups, get_split_info
)

def test_workouts_service():
    """Тестирование сервиса тренировок"""
    print("🧪 Тестирование сервиса тренировок...")
    
    # Тест 1: Проверка классов
    print("✅ Классы загружены:")
    print(f"  - WorkoutGoal: {list(WorkoutGoal)}")
    print(f"  - WorkoutLevel: {list(WorkoutLevel)}")
    print(f"  - EquipmentType: {list(EquipmentType)}")
    
    # Тест 2: Проверка базы данных упражнений
    print("\n✅ База данных упражнений:")
    for muscle_group, levels in EXERCISES_DATABASE.items():
        print(f"  - {muscle_group}: {len(levels)} уровней")
        for level, exercises in levels.items():
            print(f"    {level.value}: {len(exercises)} упражнений")
    
    # Тест 3: Проверка функций
    print("\n✅ Функции:")
    muscle_groups = get_muscle_groups()
    print(f"  - get_muscle_groups(): {muscle_groups}")
    
    split_info = get_split_info()
    print(f"  - get_split_info(): {len(split_info)} сплитов")
    
    # Тест 4: Проверка генерации плана
    print("\n✅ Генерация плана тренировок:")
    try:
        workout_plan = generate_workout_plan(
            user_weight=70.0,
            user_height=175,
            user_gender="male",
            user_age=25,
            goal=WorkoutGoal.TONE,
            level=WorkoutLevel.BEGINNER,
            available_equipment=[EquipmentType.BODYWEIGHT, EquipmentType.DUMBBELLS]
        )
        print(f"  - План сгенерирован: {len(workout_plan)} дней")
        for day, plan in workout_plan.items():
            exercises_count = len(plan.get("exercises", []))
            print(f"    {day}: {exercises_count} упражнений")
    except Exception as e:
        print(f"  ❌ Ошибка генерации плана: {e}")
    
    # Тест 5: Проверка получения упражнений
    print("\n✅ Получение упражнений:")
    exercises = get_exercises_for_muscle_group("chest", WorkoutLevel.BEGINNER)
    print(f"  - Упражнения для груди (beginner): {len(exercises)}")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_workouts_service()