#!/usr/bin/env python3
"""
Скрипт для проверки утилит
"""

import sys
import os
import inspect

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_utils():
    """Проверить утилиты на ошибки"""
    print("🔍 Проверка утилит...")
    
    utils_to_check = [
        'app.utils.chat_cleanup',
        'app.utils.video_utils',
        'app.utils.db_utils',
        'app.utils.rewards_utils',
        'app.utils.broadcast_utils',
        'app.utils.nutrition_utils'
    ]
    
    errors = []
    success_count = 0
    
    for util_name in utils_to_check:
        try:
            module = __import__(util_name, fromlist=['*'])
            
            # Проверяем основные функции
            if util_name == 'app.utils.chat_cleanup':
                required_items = [
                    'cleanup_start_messages', 'cleanup_cabinet_messages',
                    'cleanup_workout_messages', 'cleanup_menu_messages'
                ]
                
            elif util_name == 'app.utils.video_utils':
                required_items = [
                    'VideoManager', 'send_exercise_demo', 'send_workout_plan_with_media'
                ]
                
            elif util_name == 'app.utils.db_utils':
                required_items = [
                    'get_user_by_tg_id', 'user_has_paid_access', 'add_stars_to_user'
                ]
                
            elif util_name == 'app.utils.rewards_utils':
                required_items = [
                    'RewardsManager', 'motivation_manager'
                ]
                
            elif util_name == 'app.utils.broadcast_utils':
                required_items = [
                    'BroadcastManager', 'NotificationManager'
                ]
                
            elif util_name == 'app.utils.nutrition_utils':
                required_items = [
                    'NutritionCalculator', 'MealPlanner', 'NutritionAnalyzer'
                ]
            
            # Проверяем наличие функций
            for item in required_items:
                if not hasattr(module, item):
                    raise AttributeError(f"Отсутствует {item}")
            
            print(f"✅ {util_name}: {len(required_items)} функций")
            success_count += 1
            
        except Exception as e:
            error_msg = f"❌ {util_name}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n📊 Результаты проверки утилит:")
    print(f"  ✅ Успешно: {success_count}")
    print(f"  ❌ Ошибок: {len(errors)}")
    
    if errors:
        print(f"\n❌ Ошибки утилит:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ Все утилиты в порядке")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_utils()
    sys.exit(0 if success else 1)