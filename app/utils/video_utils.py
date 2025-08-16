import os
import asyncio
from typing import Dict, List, Optional
from aiogram import types
from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class VideoManager:
    """Менеджер для работы с видео упражнений"""

    def __init__(self, video_dir: str = "assets/videos", image_dir: str = "assets/images"):
        self.video_dir = video_dir
        self.image_dir = image_dir
        self.video_cache: Dict[str, str] = {}
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Создает директории для видео и изображений"""
        for directory in [self.video_dir, self.image_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def get_video_path(self, exercise_name: str, muscle_group: str, level: str) -> str:
        """Получает путь к видео упражнения"""
        clean_name = "".join(c for c in exercise_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_').lower()
        filename = f"{muscle_group}_{level}_{clean_name}.mp4"
        return os.path.join(self.video_dir, filename)

    def get_image_path(self, exercise_name: str, muscle_group: str, level: str) -> str:
        """Получает путь к изображению упражнения"""
        clean_name = "".join(c for c in exercise_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_').lower()
        filename = f"{muscle_group}_{level}_{clean_name}.jpg"
        return os.path.join(self.image_dir, "exercises", muscle_group, filename)

    def video_exists(self, exercise_name: str, muscle_group: str, level: str) -> bool:
        """Проверяет, существует ли видео упражнения"""
        video_path = self.get_video_path(exercise_name, muscle_group, level)
        return os.path.exists(video_path)

    def image_exists(self, exercise_name: str, muscle_group: str, level: str) -> bool:
        """Проверяет, существует ли изображение упражнения"""
        image_path = self.get_image_path(exercise_name, muscle_group, level)
        return os.path.exists(image_path)

    def get_video_url(self, exercise_name: str, muscle_group: str, level: str) -> str:
        """Получает URL видео упражнения с водяным знаком"""
        clean_name = "".join(c for c in exercise_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_').lower()
        return f"https://youtu.be/{muscle_group}_{level}_{clean_name}"

    def get_image_url(self, exercise_name: str, muscle_group: str, level: str) -> str:
        """Получает URL изображения упражнения"""
        clean_name = "".join(c for c in exercise_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_').lower()
        return f"https://fitcoach.com/images/exercises/{muscle_group}/{level}_{clean_name}.jpg"

    async def add_watermark_to_image(self, image_path: str, watermark_text: str = "FitCoach") -> str:
        """Добавляет водяной знак к изображению"""
        try:
            # Открываем изображение
            with Image.open(image_path) as img:
                # Создаем копию для редактирования
                img_copy = img.copy()
                draw = ImageDraw.Draw(img_copy)
                
                # Настраиваем шрифт
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except:
                    font = ImageFont.load_default()
                
                # Получаем размеры изображения
                width, height = img_copy.size
                
                # Позиция водяного знака (правый нижний угол)
                text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                x = width - text_width - 20
                y = height - text_height - 20
                
                # Добавляем полупрозрачный фон
                padding = 10
                draw.rectangle(
                    [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                    fill=(0, 0, 0, 128)
                )
                
                # Добавляем текст
                draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 255))
                
                # Сохраняем с водяным знаком
                watermarked_path = image_path.replace('.jpg', '_watermarked.jpg')
                img_copy.save(watermarked_path, 'JPEG', quality=95)
                
                return watermarked_path
                
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return image_path

    async def send_exercise_video(
        self,
        message: types.Message,
        exercise_name: str,
        muscle_group: str,
        level: str,
        description: str = "",
        target_muscles: List[str] = None
    ) -> bool:
        """Отправляет видео упражнения с водяным знаком"""
        video_path = self.get_video_path(exercise_name, muscle_group, level)

        if os.path.exists(video_path):
            try:
                video = FSInputFile(video_path)
                caption = self._create_exercise_caption(exercise_name, description, target_muscles)
                await message.answer_video(video, caption=caption, parse_mode="HTML")
                return True
            except Exception as e:
                print(f"Error sending video {video_path}: {e}")
                return False
        else:
            # Отправляем ссылку на YouTube с водяным знаком
            video_url = self.get_video_url(exercise_name, muscle_group, level)
            caption = self._create_exercise_caption(exercise_name, description, target_muscles)
            caption += f"\n\n🎥 <a href='{video_url}'>Смотреть видео на YouTube</a>"
            await message.answer(caption, parse_mode="HTML", disable_web_page_preview=True)
            return True

    async def send_exercise_image(
        self,
        message: types.Message,
        exercise_name: str,
        muscle_group: str,
        level: str,
        description: str = "",
        target_muscles: List[str] = None,
        instructions: List[str] = None
    ) -> bool:
        """Отправляет изображение упражнения с водяным знаком"""
        image_path = self.get_image_path(exercise_name, muscle_group, level)

        if os.path.exists(image_path):
            try:
                # Добавляем водяной знак
                watermarked_path = await self.add_watermark_to_image(image_path)
                photo = FSInputFile(watermarked_path)
                caption = self._create_exercise_caption(exercise_name, description, target_muscles, instructions)
                await message.answer_photo(photo, caption=caption, parse_mode="HTML")
                return True
            except Exception as e:
                print(f"Error sending image {image_path}: {e}")
                return False
        else:
            # Отправляем текстовое описание
            caption = self._create_exercise_caption(exercise_name, description, target_muscles, instructions)
            caption += "\n\n📝 <i>Изображение упражнения будет добавлено позже</i>"
            await message.answer(caption, parse_mode="HTML")
            return True

    def _create_exercise_caption(
        self,
        exercise_name: str,
        description: str = "",
        target_muscles: List[str] = None,
        instructions: List[str] = None
    ) -> str:
        """Создает подпись для упражнения"""
        caption = f"🏋️‍♂️ <b>{exercise_name}</b>\n\n"
        
        if description:
            caption += f"{description}\n\n"
        
        if target_muscles:
            caption += f"🎯 <b>Целевые мышцы:</b>\n"
            for muscle in target_muscles:
                caption += f"• {muscle}\n"
            caption += "\n"
        
        if instructions:
            caption += f"📋 <b>Техника выполнения:</b>\n"
            for i, instruction in enumerate(instructions, 1):
                caption += f"{i}. {instruction}\n"
            caption += "\n"
        
        caption += "💪 <b>FitCoach</b> - ваш персональный тренер!"
        
        return caption

    async def send_exercise_demo(
        self,
        message: types.Message,
        exercise_name: str,
        muscle_group: str,
        level: str,
        description: str = "",
        target_muscles: List[str] = None,
        instructions: List[str] = None,
        prefer_video: bool = True
    ) -> bool:
        """Отправляет демонстрацию упражнения (видео или изображение)"""
        if prefer_video:
            if await self.send_exercise_video(message, exercise_name, muscle_group, level, description, target_muscles):
                return True
            return await self.send_exercise_image(message, exercise_name, muscle_group, level, description, target_muscles, instructions)
        else:
            if await self.send_exercise_image(message, exercise_name, muscle_group, level, description, target_muscles, instructions):
                return True
            return await self.send_exercise_video(message, exercise_name, muscle_group, level, description, target_muscles)

    async def send_workout_plan_with_media(
        self,
        message: types.Message,
        workout_plan: Dict,
        day: str
    ) -> bool:
        """Отправляет план тренировки с медиа"""
        if day not in workout_plan:
            await message.answer("День не найден в плане тренировок")
            return False
        
        day_plan = workout_plan[day]
        if not day_plan.get("exercises"):
            await message.answer(f"На {day} запланирован отдых")
            return False
        
        # Создаем медиа группу
        media_group = []
        caption = f"📋 <b>План тренировки: {day.title()}</b>\n\n"
        
        for i, exercise in enumerate(day_plan["exercises"]):
            exercise_caption = (
                f"{i+1}. <b>{exercise['name']}</b>\n"
                f"🎯 {', '.join(exercise['target_muscles'])}\n"
                f"⚖️ {exercise['sets']} x {exercise['reps']} @ {exercise['weight']}кг\n"
                f"⏱️ Отдых: {exercise['rest_time']} сек\n"
                f"📝 {exercise['description']}\n\n"
            )
            
            if i == 0:  # Первое упражнение с основной подписью
                full_caption = caption + exercise_caption
            else:
                full_caption = exercise_caption
            
            # Добавляем изображение или видео
            if self.image_exists(exercise['name'], exercise['muscle_group'], exercise.get('level', 'beginner')):
                image_path = self.get_image_path(exercise['name'], exercise['muscle_group'], exercise.get('level', 'beginner'))
                watermarked_path = await self.add_watermark_to_image(image_path)
                media_group.append(InputMediaPhoto(
                    media=FSInputFile(watermarked_path),
                    caption=full_caption,
                    parse_mode="HTML"
                ))
            else:
                # Если нет изображения, отправляем текстовое описание
                await message.answer(full_caption, parse_mode="HTML")
        
        # Отправляем медиа группу
        if media_group:
            await message.answer_media_group(media_group)
        
        return True

# Глобальный экземпляр менеджера видео
video_manager = VideoManager()

# Функции для удобства использования
async def send_exercise_demo(
    message: types.Message,
    exercise_name: str,
    muscle_group: str,
    level: str,
    description: str = "",
    target_muscles: List[str] = None,
    instructions: List[str] = None,
    prefer_video: bool = True
) -> bool:
    """Отправляет демонстрацию упражнения"""
    return await video_manager.send_exercise_demo(
        message, exercise_name, muscle_group, level, description, target_muscles, instructions, prefer_video
    )

async def send_workout_plan_with_media(
    message: types.Message,
    workout_plan: Dict,
    day: str
) -> bool:
    """Отправляет план тренировки с медиа"""
    return await video_manager.send_workout_plan_with_media(message, workout_plan, day)

def get_exercise_video_url(exercise_name: str, muscle_group: str, level: str) -> str:
    """Получает URL видео упражнения"""
    return video_manager.get_video_url(exercise_name, muscle_group, level)

def get_exercise_image_url(exercise_name: str, muscle_group: str, level: str) -> str:
    """Получает URL изображения упражнения"""
    return video_manager.get_image_url(exercise_name, muscle_group, level)

def exercise_has_video(exercise_name: str, muscle_group: str, level: str) -> bool:
    """Проверяет, есть ли видео для упражнения"""
    return video_manager.video_exists(exercise_name, muscle_group, level)

def exercise_has_image(exercise_name: str, muscle_group: str, level: str) -> bool:
    """Проверяет, есть ли изображение для упражнения"""
    return video_manager.image_exists(exercise_name, muscle_group, level)