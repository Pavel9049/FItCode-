#!/usr/bin/env python3
"""
Скрипт для генерации тестовых изображений упражнений и блюд с водяными знаками
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random

def create_test_image(width: int, height: int, text: str, filename: str, watermark: str = "FitCoach"):
    """Создать тестовое изображение с текстом и водяным знаком"""
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), color=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
    draw = ImageDraw.Draw(img)
    
    # Настраиваем шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 48)
        small_font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Добавляем основной текст
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Добавляем фон для текста
    padding = 20
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill=(255, 255, 255, 200)
    )
    
    # Добавляем текст
    draw.text((x, y), text, font=font, fill=(0, 0, 0))
    
    # Добавляем водяной знак
    watermark_bbox = draw.textbbox((0, 0), watermark, font=small_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    watermark_height = watermark_bbox[3] - watermark_bbox[1]
    
    watermark_x = width - watermark_width - 20
    watermark_y = height - watermark_height - 20
    
    # Полупрозрачный фон для водяного знака
    draw.rectangle(
        [watermark_x - 10, watermark_y - 10, watermark_x + watermark_width + 10, watermark_y + watermark_height + 10],
        fill=(0, 0, 0, 128)
    )
    
    # Водяной знак
    draw.text((watermark_x, watermark_y), watermark, font=small_font, fill=(255, 255, 255))
    
    # Сохраняем изображение
    img.save(filename, 'JPEG', quality=95)
    print(f"Создано изображение: {filename}")

def generate_exercise_images():
    """Генерировать изображения упражнений"""
    
    exercises = {
        "chest": {
            "beginner": [
                "Отжимания от пола",
                "Жим гантелей лежа"
            ],
            "novice": [
                "Жим штанги лежа",
                "Разведение гантелей лежа"
            ],
            "advanced": [
                "Жим штанги на наклонной скамье",
                "Отжимания на брусьях"
            ],
            "pro": [
                "Жим штанги с паузами",
                "Жим гантелей на наклонной скамье с дроп-сетами"
            ]
        },
        "back": {
            "beginner": [
                "Подтягивания с резинкой",
                "Тяга гантели в наклоне"
            ],
            "novice": [
                "Подтягивания на турнике",
                "Тяга штанги в наклоне"
            ],
            "advanced": [
                "Подтягивания широким хватом",
                "Тяга Т-грифа"
            ],
            "pro": [
                "Подтягивания с отягощением",
                "Тяга штанги в наклоне с паузами"
            ]
        },
        "legs": {
            "beginner": [
                "Приседания с собственным весом",
                "Выпады"
            ],
            "novice": [
                "Приседания с гантелями",
                "Жим ногами"
            ],
            "advanced": [
                "Приседания со штангой",
                "Становая тяга"
            ],
            "pro": [
                "Приседания с паузами",
                "Становая тяга с дефицитом"
            ]
        },
        "shoulders": {
            "beginner": [
                "Отжимания от стены",
                "Жим гантелей стоя"
            ],
            "novice": [
                "Жим штанги стоя",
                "Разведение гантелей в стороны"
            ],
            "advanced": [
                "Жим Арнольда",
                "Тяга к подбородку"
            ],
            "pro": [
                "Жим с паузами",
                "Разведение с дроп-сетами"
            ]
        },
        "biceps": {
            "beginner": [
                "Подтягивания обратным хватом",
                "Сгибания с гантелями"
            ],
            "novice": [
                "Подъем штанги на бицепс",
                "Молотки"
            ],
            "advanced": [
                "Концентрированные сгибания",
                "Сгибания на скамье Скотта"
            ],
            "pro": [
                "Сгибания с паузами",
                "Дроп-сеты на бицепс"
            ]
        },
        "triceps": {
            "beginner": [
                "Отжимания от пола узким хватом",
                "Разгибания с гантелями"
            ],
            "novice": [
                "Жим узким хватом",
                "Разгибания на блоке"
            ],
            "advanced": [
                "Отжимания на брусьях",
                "Разгибания из-за головы"
            ],
            "pro": [
                "Разгибания с паузами",
                "Дроп-сеты на трицепс"
            ]
        },
        "abs": {
            "beginner": [
                "Скручивания",
                "Планка"
            ],
            "novice": [
                "Скручивания с подъемом ног",
                "Боковая планка"
            ],
            "advanced": [
                "Подъемы ног в висе",
                "Русские скручивания"
            ],
            "pro": [
                "Скручивания с отягощением",
                "Планка с движениями"
            ]
        }
    }
    
    for muscle_group, levels in exercises.items():
        for level, exercise_list in levels.items():
            for exercise in exercise_list:
                filename = f"assets/images/exercises/{muscle_group}/{muscle_group}_{level}_{exercise.replace(' ', '_').lower()}.jpg"
                create_test_image(800, 600, exercise, filename)

def generate_meal_images():
    """Генерировать изображения блюд"""
    
    meals = {
        "breakfast": [
            "Овсянка с ягодами и орехами",
            "Творожная запеканка с фруктами",
            "Протеиновый смузи с бананом",
            "Яичница с овощами"
        ],
        "lunch": [
            "Куриная грудка с овощами и рисом",
            "Лосось с киноа и овощами",
            "Салат с тунцом и авокадо",
            "Суп с курицей и овощами"
        ],
        "dinner": [
            "Индейка с гречкой и овощами",
            "Творог с фруктами и орехами",
            "Омлет с овощами и сыром",
            "Запеченная рыба с овощами"
        ],
        "snack": [
            "Протеиновый коктейль с бананом",
            "Орехи и сухофрукты",
            "Йогурт с ягодами и медом",
            "Творожная масса с фруктами"
        ]
    }
    
    for meal_type, meal_list in meals.items():
        for meal in meal_list:
            filename = f"assets/images/meals/{meal_type}/{meal.replace(' ', '_').lower()}.jpg"
            create_test_image(800, 600, meal, filename)

def main():
    """Основная функция"""
    print("Генерация тестовых изображений...")
    
    # Создаем директории если их нет
    os.makedirs("assets/images/exercises/chest", exist_ok=True)
    os.makedirs("assets/images/exercises/back", exist_ok=True)
    os.makedirs("assets/images/meals/breakfast", exist_ok=True)
    os.makedirs("assets/images/meals/lunch", exist_ok=True)
    os.makedirs("assets/images/meals/dinner", exist_ok=True)
    os.makedirs("assets/images/meals/snack", exist_ok=True)
    
    # Генерируем изображения
    generate_exercise_images()
    generate_meal_images()
    
    print("Генерация завершена!")

if __name__ == "__main__":
    main()