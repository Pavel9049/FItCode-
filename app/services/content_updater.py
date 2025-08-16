#!/usr/bin/env python3
"""
Сервис для обновления контента из JSON файлов
"""

import json
import os
from typing import Dict, List, Any
from app.db.session import get_session_maker
from app.db.models import Exercise, Meal, ProgramLevel
from app.services.workouts import WorkoutLevel, EquipmentType, Exercise as WorkoutExercise
from app.services.nutrition import MealType, Meal as NutritionMeal
from sqlalchemy import text


class ContentUpdater:
    """Сервис для обновления контента"""
    
    def __init__(self):
        self.async_session = get_session_maker()
    
    async def update_workouts_from_json(self, json_file_path: str = "new_workouts.json") -> Dict[str, Any]:
        """Обновить тренировки из JSON файла"""
        if not os.path.exists(json_file_path):
            return {"success": False, "message": "Файл не найден", "added": 0}
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                workouts_data = json.load(f)
            
            added_count = 0
            errors = []
            
            async with self.async_session() as session:
                for workout in workouts_data:
                    try:
                        # Проверяем, не существует ли уже такое упражнение
                        existing = await session.execute(
                            text("SELECT id FROM exercises WHERE name = :name AND level = :level"),
                            {"name": workout["name"], "level": workout["level"]}
                        )
                        
                        if existing.scalar():
                            continue  # Пропускаем, если уже существует
                        
                        # Создаем новое упражнение
                        new_exercise = Exercise(
                            name=workout["name"],
                            muscle_group=workout["muscle_group"],
                            level=ProgramLevel(workout["level"]),
                            requires_equipment=workout.get("requires_equipment", False),
                            video_url=workout.get("video_url", ""),
                            description=workout.get("description", "")
                        )
                        
                        session.add(new_exercise)
                        added_count += 1
                        
                    except Exception as e:
                        errors.append(f"Ошибка добавления {workout.get('name', 'Unknown')}: {e}")
                
                await session.commit()
            
            # Перемещаем обработанный файл в архив
            archive_path = f"processed_workouts_{int(os.path.getmtime(json_file_path))}.json"
            os.rename(json_file_path, archive_path)
            
            return {
                "success": True,
                "message": f"Добавлено {added_count} новых упражнений",
                "added": added_count,
                "errors": errors,
                "archived": archive_path
            }
            
        except Exception as e:
            return {"success": False, "message": f"Ошибка обработки файла: {e}", "added": 0}
    
    async def update_nutrition_from_json(self, json_file_path: str = "new_nutrition.json") -> Dict[str, Any]:
        """Обновить питание из JSON файла"""
        if not os.path.exists(json_file_path):
            return {"success": False, "message": "Файл не найден", "added": 0}
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                nutrition_data = json.load(f)
            
            added_count = 0
            errors = []
            
            async with self.async_session() as session:
                for meal in nutrition_data:
                    try:
                        # Проверяем, не существует ли уже такое блюдо
                        existing = await session.execute(
                            text("SELECT id FROM meals WHERE title = :title"),
                            {"title": meal["title"]}
                        )
                        
                        if existing.scalar():
                            continue  # Пропускаем, если уже существует
                        
                        # Создаем новое блюдо
                        new_meal = Meal(
                            title=meal["title"],
                            photo_url=meal.get("photo_url", ""),
                            kcal=meal["kcal"],
                            proteins=meal["proteins"],
                            fats=meal["fats"],
                            carbs=meal["carbs"],
                            recipe=meal.get("recipe", ""),
                            article_url=meal.get("article_url", ""),
                            tags=meal.get("tags", "")
                        )
                        
                        session.add(new_meal)
                        added_count += 1
                        
                    except Exception as e:
                        errors.append(f"Ошибка добавления {meal.get('title', 'Unknown')}: {e}")
                
                await session.commit()
            
            # Перемещаем обработанный файл в архив
            archive_path = f"processed_nutrition_{int(os.path.getmtime(json_file_path))}.json"
            os.rename(json_file_path, archive_path)
            
            return {
                "success": True,
                "message": f"Добавлено {added_count} новых блюд",
                "added": added_count,
                "errors": errors,
                "archived": archive_path
            }
            
        except Exception as e:
            return {"success": False, "message": f"Ошибка обработки файла: {e}", "added": 0}
    
    async def get_content_stats(self) -> Dict[str, Any]:
        """Получить статистику контента"""
        try:
            async with self.async_session() as session:
                # Статистика упражнений
                exercises_result = await session.execute(
                    text("SELECT muscle_group, level, COUNT(*) FROM exercises GROUP BY muscle_group, level")
                )
                exercises_stats = exercises_result.fetchall()
                
                # Статистика блюд
                meals_result = await session.execute(
                    text("SELECT COUNT(*) FROM meals")
                )
                meals_count = meals_result.scalar()
                
                # Статистика программ
                programs_result = await session.execute(
                    text("SELECT COUNT(*) FROM programs")
                )
                programs_count = programs_result.scalar()
                
                return {
                    "exercises": exercises_stats,
                    "meals_count": meals_count,
                    "programs_count": programs_count
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def create_sample_workouts_json(self, filename: str = "sample_workouts.json"):
        """Создать пример JSON файла с тренировками"""
        sample_workouts = [
            {
                "name": "Жим штанги стоя",
                "muscle_group": "shoulders",
                "level": "advanced",
                "requires_equipment": True,
                "video_url": "https://youtu.be/sample_shoulder_press",
                "description": "Базовое упражнение для развития плеч"
            },
            {
                "name": "Приседания с гантелями",
                "muscle_group": "legs",
                "level": "novice",
                "requires_equipment": True,
                "video_url": "https://youtu.be/sample_dumbbell_squats",
                "description": "Приседания с гантелями для развития ног"
            }
        ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample_workouts, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def create_sample_nutrition_json(self, filename: str = "sample_nutrition.json"):
        """Создать пример JSON файла с питанием"""
        sample_nutrition = [
            {
                "title": "Куриная грудка с овощами",
                "kcal": 250,
                "proteins": 30.0,
                "fats": 8.0,
                "carbs": 15.0,
                "recipe": "1. Обжарьте куриную грудку\n2. Добавьте овощи\n3. Подавайте горячим",
                "photo_url": "assets/images/meals/lunch/chicken_vegetables.jpg",
                "tags": "белок,обед,курица"
            },
            {
                "title": "Протеиновый коктейль с бананом",
                "kcal": 180,
                "proteins": 25.0,
                "fats": 3.0,
                "carbs": 20.0,
                "recipe": "1. Смешайте протеин с молоком\n2. Добавьте банан\n3. Взбейте в блендере",
                "photo_url": "assets/images/meals/snack/protein_shake.jpg",
                "tags": "белок,перекус,протеин"
            }
        ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample_nutrition, f, ensure_ascii=False, indent=2)
        
        return filename


# Глобальный экземпляр
content_updater = ContentUpdater()