#!/usr/bin/env python3
"""
Скрипт для проверки синтаксиса всех Python файлов
"""

import ast
import os
import sys

def check_syntax():
    """Проверить синтаксис всех Python файлов"""
    print("🔍 Проверка синтаксиса Python файлов...")
    
    errors = []
    files_checked = 0
    
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                files_checked += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        ast.parse(content)
                except SyntaxError as e:
                    errors.append(f"{file_path}: {e}")
                except Exception as e:
                    errors.append(f"{file_path}: {e}")
    
    print(f"📊 Проверено файлов: {files_checked}")
    
    if errors:
        print(f"❌ Найдено ошибок: {len(errors)}")
        for error in errors:
            print(f"  {error}")
    else:
        print("✅ Синтаксических ошибок не найдено")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_syntax()
    sys.exit(0 if success else 1)