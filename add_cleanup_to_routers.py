#!/usr/bin/env python3
"""
Скрипт для добавления очистки сообщений во все роутеры
"""

import os
import re

def add_cleanup_to_router(router_file, cleanup_function):
    """Добавляет очистку сообщений в роутер"""
    
    if not os.path.exists(router_file):
        print(f"Файл {router_file} не найден")
        return
    
    with open(router_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем импорт
    if 'from app.utils.chat_cleanup import' not in content:
        import_line = 'from app.utils.chat_cleanup import cleanup_general_messages'
        content = content.replace('from aiogram import Router', f'from aiogram import Router\nfrom app.utils.chat_cleanup import {cleanup_function}')
    
    # Добавляем очистку в обработчики команд
    content = re.sub(
        r'@router\.message\(Command\("([^"]+)"\)\)\s*\nasync def (\w+)\(message: types\.Message\):\s*\n\s*"""([^"]*)"""\s*\n\s*await (\w+)\(message\)',
        r'@router.message(Command("\1"))\nasync def \2(message: types.Message):\n\t"""\3"""\n\tawait cleanup_general_messages(message)\n\tawait \4(message)',
        content
    )
    
    # Добавляем очистку в callback обработчики
    content = re.sub(
        r'@router\.callback_query\(lambda c: c\.data == "([^"]+)"\)\s*\nasync def (\w+)\(callback: types\.CallbackQuery\):\s*\n\s*"""([^"]*)"""\s*\n\s*await (\w+)\(callback\.message\)\s*\n\s*await callback\.answer\(\)',
        r'@router.callback_query(lambda c: c.data == "\1")\nasync def \2(callback: types.CallbackQuery):\n\t"""\3"""\n\tawait cleanup_general_messages(callback.message)\n\tawait \4(callback.message)\n\tawait callback.answer()',
        content
    )
    
    with open(router_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Очистка добавлена в {router_file}")

# Список роутеров для обновления
routers = [
    ('app/routers/rewards.py', 'cleanup_rewards_messages'),
    ('app/routers/settings.py', 'cleanup_settings_messages'),
    ('app/routers/support.py', 'cleanup_support_messages'),
    ('app/routers/instagram.py', 'cleanup_instagram_messages'),
    ('app/routers/ai_kbju.py', 'cleanup_ai_kbju_messages'),
    ('app/routers/referral.py', 'cleanup_referral_messages'),
    ('app/routers/purchase.py', 'cleanup_purchase_messages'),
    ('app/routers/start.py', 'cleanup_start_messages'),
]

for router_file, cleanup_func in routers:
    add_cleanup_to_router(router_file, cleanup_func)

print("Очистка сообщений добавлена во все роутеры!")