#!/usr/bin/env python3
"""
Скрипт для проверки роутеров
"""

import sys
import os
import inspect

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_routers():
    """Проверить роутеры на ошибки"""
    print("🔍 Проверка роутеров...")
    
    routers_to_check = [
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
        'app.routers.health'
    ]
    
    errors = []
    success_count = 0
    
    for router_name in routers_to_check:
        try:
            module = __import__(router_name, fromlist=['router'])
            router = getattr(module, 'router')
            
            # Проверяем, что роутер имеет обработчики
            handlers = []
            for handler in router.message.handlers:
                handlers.append(handler.callback.__name__)
            for handler in router.callback_query.handlers:
                handlers.append(handler.callback.__name__)
            
            print(f"✅ {router_name}: {len(handlers)} обработчиков")
            success_count += 1
            
        except Exception as e:
            error_msg = f"❌ {router_name}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n📊 Результаты проверки роутеров:")
    print(f"  ✅ Успешно: {success_count}")
    print(f"  ❌ Ошибок: {len(errors)}")
    
    if errors:
        print(f"\n❌ Ошибки роутеров:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ Все роутеры в порядке")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_routers()
    sys.exit(0 if success else 1)