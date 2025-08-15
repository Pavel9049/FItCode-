#!/usr/bin/env python3
"""
Скрипт для проверки сервисов
"""

import sys
import os
import inspect

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_services():
    """Проверить сервисы на ошибки"""
    print("🔍 Проверка сервисов...")
    
    services_to_check = [
        'app.services.workouts',
        'app.services.nutrition',
        'app.services.payments',
        'app.services.bootstrap'
    ]
    
    errors = []
    success_count = 0
    
    for service_name in services_to_check:
        try:
            module = __import__(service_name, fromlist=['*'])
            
            # Проверяем основные функции
            if service_name == 'app.services.workouts':
                # Проверяем классы и функции
                required_items = [
                    'WorkoutGoal', 'WorkoutLevel', 'EquipmentType', 'Exercise',
                    'WorkoutCalculator', 'EXERCISES_DATABASE', 'generate_workout_plan',
                    'get_exercises_for_muscle_group', 'get_muscle_groups', 'get_split_info'
                ]
                
                for item in required_items:
                    if not hasattr(module, item):
                        raise AttributeError(f"Отсутствует {item}")
                
                # Проверяем базу данных упражнений
                exercises_db = getattr(module, 'EXERCISES_DATABASE')
                if not isinstance(exercises_db, dict):
                    raise TypeError("EXERCISES_DATABASE должен быть словарем")
                
                print(f"✅ {service_name}: {len(exercises_db)} групп мышц")
                
            elif service_name == 'app.services.nutrition':
                # Проверяем классы и функции
                required_items = [
                    'NutritionGoal', 'MealType', 'Meal', 'NutritionCalculator',
                    'MealPlanner', 'MEALS_DATABASE'
                ]
                
                for item in required_items:
                    if not hasattr(module, item):
                        raise AttributeError(f"Отсутствует {item}")
                
                # Проверяем базу данных блюд
                meals_db = getattr(module, 'MEALS_DATABASE')
                if not isinstance(meals_db, dict):
                    raise TypeError("MEALS_DATABASE должен быть словарем")
                
                print(f"✅ {service_name}: {len(meals_db)} типов блюд")
                
            elif service_name == 'app.services.payments':
                # Проверяем функции платежей
                required_items = [
                    'PaymentGateway'
                ]
                
                for item in required_items:
                    if not hasattr(module, item):
                        raise AttributeError(f"Отсутствует {item}")
                
                print(f"✅ {service_name}: платежные функции")
                
            elif service_name == 'app.services.bootstrap':
                # Проверяем функции инициализации
                required_items = [
                    'ensure_default_programs', 'DEFAULT_PROGRAMS'
                ]
                
                for item in required_items:
                    if not hasattr(module, item):
                        raise AttributeError(f"Отсутствует {item}")
                
                print(f"✅ {service_name}: функции инициализации")
            
            success_count += 1
            
        except Exception as e:
            error_msg = f"❌ {service_name}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n📊 Результаты проверки сервисов:")
    print(f"  ✅ Успешно: {success_count}")
    print(f"  ❌ Ошибок: {len(errors)}")
    
    if errors:
        print(f"\n❌ Ошибки сервисов:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ Все сервисы в порядке")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_services()
    sys.exit(0 if success else 1)