#!/usr/bin/env python3
"""
Скрипт для проверки импортов всех модулей
"""

import importlib
import sys
import os

def check_imports():
    """Проверить импорты всех модулей"""
    print("🔍 Проверка импортов модулей...")
    
    modules_to_check = [
        'app.config',
        'app.db.session',
        'app.db.models',
        'app.services.workouts',
        'app.services.nutrition',
        'app.services.payments',
        'app.services.bootstrap',
        'app.utils.chat_cleanup',
        'app.utils.video_utils',
        'app.utils.db_utils',
        'app.utils.rewards_utils',
        'app.utils.broadcast_utils',
        'app.utils.nutrition_utils',
        'app.routers.start',
        'app.routers.workouts',
        'app.routers.menu',
        'app.routers.cabinet',
        'app.routers.rewards',
        'app.routers.settings',
        'app.routers.support',
        'app.routers.instagram',
        'app.routers.ai_kbju',
        'app.routers.referral',
        'app.routers.purchase',
        'app.routers.payments_gateway',
        'app.routers.check_payment',
        'app.routers.admin',
        'app.routers.test',
        'app.routers.fallback',
        'app.routers.health',
        'app.background.scheduler'
    ]
    
    errors = []
    success_count = 0
    
    for module_name in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}")
            success_count += 1
        except ImportError as e:
            error_msg = f"❌ {module_name}: {e}"
            print(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"❌ {module_name}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n📊 Результаты:")
    print(f"  ✅ Успешно: {success_count}")
    print(f"  ❌ Ошибок: {len(errors)}")
    
    if errors:
        print(f"\n❌ Ошибки импорта:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ Все модули импортируются успешно")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)