#!/usr/bin/env python3
"""
Скрипт для исправления базы данных
"""

import sqlite3
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    """Исправить базу данных"""
    print("🔧 Исправление базы данных...")
    
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    try:
        # Проверяем наличие колонки notifications_enabled
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'notifications_enabled' not in columns:
            print("✅ Добавляем колонку notifications_enabled...")
            cursor.execute("ALTER TABLE users ADD COLUMN notifications_enabled BOOLEAN DEFAULT 1")
        
        # Проверяем наличие колонки article_url в meals
        cursor.execute("PRAGMA table_info(meals)")
        meal_columns = [col[1] for col in cursor.fetchall()]
        
        if 'article_url' not in meal_columns:
            print("✅ Добавляем колонку article_url в meals...")
            cursor.execute("ALTER TABLE meals ADD COLUMN article_url VARCHAR(512)")
        
        conn.commit()
        print("✅ База данных исправлена!")
        
    except Exception as e:
        print(f"❌ Ошибка исправления БД: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()