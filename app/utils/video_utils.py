import os
import asyncio
from typing import Dict, List, Optional
from aiogram import types
from aiogram.types import FSInputFile


class VideoManager:
	"""Менеджер для работы с видео упражнений"""
	
	def __init__(self, video_dir: str = "assets/videos"):
		self.video_dir = video_dir
		self.video_cache: Dict[str, str] = {}
		self._ensure_video_dir()
	
	def _ensure_video_dir(self):
		"""Создает директорию для видео, если она не существует"""
		if not os.path.exists(self.video_dir):
			os.makedirs(self.video_dir, exist_ok=True)
	
	def get_video_path(self, exercise_name: str, muscle_group: str, level: str) -> str:
		"""Получает путь к видео упражнения"""
		# Очищаем название упражнения от специальных символов
		clean_name = "".join(c for c in exercise_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
		clean_name = clean_name.replace(' ', '_').lower()
		
		filename = f"{muscle_group}_{level}_{clean_name}.mp4"
		return os.path.join(self.video_dir, filename)
	
	def video_exists(self, exercise_name: str, muscle_group: str, level: str) -> bool:
		"""Проверяет, существует ли видео упражнения"""
		video_path = self.get_video_path(exercise_name, muscle_group, level)
		return os.path.exists(video_path)
	
	def get_video_url(self, exercise_name: str, muscle_group: str, level: str) -> str:
		"""Получает URL видео упражнения"""
		# В реальном проекте здесь должна быть логика получения URL из базы данных
		# или генерации ссылки на YouTube/Telegram
		
		# Пока что возвращаем заглушку
		clean_name = "".join(c for c in exercise_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
		clean_name = clean_name.replace(' ', '_').lower()
		
		return f"https://youtu.be/{muscle_group}_{level}_{clean_name}"
	
	async def send_exercise_video(
		self, 
		message: types.Message, 
		exercise_name: str, 
		muscle_group: str, 
		level: str,
		description: str = ""
	) -> bool:
		"""
		Отправляет видео упражнения
		
		Returns:
			bool: True если видео отправлено, False если видео не найдено
		"""
		video_path = self.get_video_path(exercise_name, muscle_group, level)
		
		if os.path.exists(video_path):
			try:
				video = FSInputFile(video_path)
				caption = f"🎥 <b>{exercise_name}</b>\n\n{description}" if description else f"🎥 <b>{exercise_name}</b>"
				await message.answer_video(video, caption=caption, parse_mode="HTML")
				return True
			except Exception as e:
				print(f"Error sending video {video_path}: {e}")
				return False
		else:
			# Если видео нет, отправляем ссылку на YouTube
			video_url = self.get_video_url(exercise_name, muscle_group, level)
			text = (
				f"🎥 <b>{exercise_name}</b>\n\n"
				f"{description}\n\n"
				f"<a href='{video_url}'>Смотреть видео на YouTube</a>"
			)
			await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
			return True
	
	async def send_exercise_thumbnail(
		self, 
		message: types.Message, 
		exercise_name: str, 
		muscle_group: str, 
		level: str,
		description: str = ""
	) -> bool:
		"""
		Отправляет превью упражнения (картинка + описание)
		
		Returns:
			bool: True если превью отправлено, False если не найдено
		"""
		# Путь к превью (картинке)
		preview_path = self.get_video_path(exercise_name, muscle_group, level).replace('.mp4', '.jpg')
		
		if os.path.exists(preview_path):
			try:
				photo = FSInputFile(preview_path)
				caption = f"🏋️‍♂️ <b>{exercise_name}</b>\n\n{description}" if description else f"🏋️‍♂️ <b>{exercise_name}</b>"
				await message.answer_photo(photo, caption=caption, parse_mode="HTML")
				return True
			except Exception as e:
				print(f"Error sending preview {preview_path}: {e}")
				return False
		else:
			# Если превью нет, отправляем текстовое описание
			text = (
				f"🏋️‍♂️ <b>{exercise_name}</b>\n\n"
				f"{description}\n\n"
				f"📝 <i>Видео демонстрация будет добавлена позже</i>"
			)
			await message.answer(text, parse_mode="HTML")
			return True


# Глобальный экземпляр менеджера видео
video_manager = VideoManager()


async def send_exercise_demo(
	message: types.Message,
	exercise_name: str,
	muscle_group: str,
	level: str,
	description: str = "",
	prefer_video: bool = True
) -> bool:
	"""
	Отправляет демонстрацию упражнения (видео или превью)
	
	Args:
		message: Сообщение для ответа
		exercise_name: Название упражнения
		muscle_group: Группа мышц
		level: Уровень сложности
		description: Описание упражнения
		prefer_video: Предпочитать ли видео над превью
	
	Returns:
		bool: True если демонстрация отправлена
	"""
	if prefer_video:
		# Сначала пробуем отправить видео
		if await video_manager.send_exercise_video(message, exercise_name, muscle_group, level, description):
			return True
		# Если видео нет, отправляем превью
		return await video_manager.send_exercise_thumbnail(message, exercise_name, muscle_group, level, description)
	else:
		# Сначала пробуем отправить превью
		if await video_manager.send_exercise_thumbnail(message, exercise_name, muscle_group, level, description):
			return True
		# Если превью нет, отправляем видео
		return await video_manager.send_exercise_video(message, exercise_name, muscle_group, level, description)


def get_exercise_video_url(exercise_name: str, muscle_group: str, level: str) -> str:
	"""
	Получает URL видео упражнения
	
	Args:
		exercise_name: Название упражнения
		muscle_group: Группа мышц
		level: Уровень сложности
	
	Returns:
		str: URL видео
	"""
	return video_manager.get_video_url(exercise_name, muscle_group, level)


def exercise_has_video(exercise_name: str, muscle_group: str, level: str) -> bool:
	"""
	Проверяет, есть ли видео для упражнения
	
	Args:
		exercise_name: Название упражнения
		muscle_group: Группа мышц
		level: Уровень сложности
	
	Returns:
		bool: True если видео есть
	"""
	return video_manager.video_exists(exercise_name, muscle_group, level)


async def send_exercise_list_with_videos(
	message: types.Message,
	exercises: List[Dict],
	muscle_group: str,
	level: str,
	title: str = "Упражнения"
) -> None:
	"""
	Отправляет список упражнений с возможностью просмотра видео
	
	Args:
		message: Сообщение для ответа
		exercises: Список упражнений
		muscle_group: Группа мышц
		level: Уровень сложности
		title: Заголовок списка
	"""
	from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
	
	text = f"🏋️‍♂️ <b>{title}</b>\n\n"
	
	buttons = []
	for i, exercise in enumerate(exercises, 1):
		text += f"<b>{i}.</b> {exercise['name']}\n"
		if exercise.get('description'):
			text += f"   {exercise['description']}\n"
		text += "\n"
		
		# Кнопка для просмотра видео
		buttons.append([
			InlineKeyboardButton(
				text=f"🎥 {exercise['name']}", 
				callback_data=f"watch_video:{muscle_group}:{level}:{i-1}"
			)
		])
	
	# Кнопка "Назад"
	buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"muscle_group:{muscle_group}")])
	
	kb = InlineKeyboardMarkup(inline_keyboard=buttons)
	await message.edit_text(text, reply_markup=kb, parse_mode="HTML")


async def handle_video_callback(
	callback: types.CallbackQuery,
	exercises: List[Dict],
	muscle_group: str,
	level: str
) -> None:
	"""
	Обрабатывает callback для просмотра видео упражнения
	
	Args:
		callback: Callback запрос
		exercises: Список упражнений
		muscle_group: Группа мышц
		level: Уровень сложности
	"""
	parts = callback.data.split(":")
	exercise_index = int(parts[3])
	
	if 0 <= exercise_index < len(exercises):
		exercise = exercises[exercise_index]
		await send_exercise_demo(
			callback.message,
			exercise['name'],
			muscle_group,
			level,
			exercise.get('description', '')
		)
	
	await callback.answer()