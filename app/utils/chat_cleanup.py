from aiogram import types
from typing import Optional, List
import asyncio


async def cleanup_old_messages(
	message: types.Message, 
	keep_pinned: bool = True, 
	max_messages: int = 50,
	exclude_callback_data: Optional[List[str]] = None
) -> None:
	"""
	Удаляет старые сообщения в чате, оставляя закрепленные и исключая определенные callback_data
	
	Args:
		message: Сообщение, от которого нужно очистить чат
		keep_pinned: Сохранять ли закрепленные сообщения
		max_messages: Максимальное количество сообщений для удаления за раз
		exclude_callback_data: Список callback_data, которые не нужно удалять
	"""
	if exclude_callback_data is None:
		exclude_callback_data = []
	
	try:
		# Получаем историю сообщений
		chat_id = message.chat.id
		user_id = message.from_user.id
		
		# Получаем последние сообщения
		async for msg in message.bot.get_chat_history(chat_id, limit=max_messages):
			# Пропускаем сообщения других пользователей
			if msg.from_user.id != user_id:
				continue
			
			# Пропускаем закрепленные сообщения
			if keep_pinned and msg.is_automatic_forward:
				continue
			
			# Пропускаем сообщения с исключенными callback_data
			if msg.reply_markup:
				for row in msg.reply_markup.inline_keyboard:
					for button in row:
						if button.callback_data:
							for excluded_data in exclude_callback_data:
								if button.callback_data.startswith(excluded_data):
									continue
			
			# Удаляем сообщение
			try:
				await msg.delete()
				await asyncio.sleep(0.1)  # Небольшая задержка между удалениями
			except Exception:
				# Игнорируем ошибки при удалении (например, сообщение уже удалено)
				pass
				
	except Exception as e:
		# Логируем ошибку, но не прерываем выполнение
		print(f"Error cleaning up messages: {e}")


async def cleanup_specific_messages(
	message: types.Message,
	callback_data_patterns: List[str],
	max_messages: int = 100
) -> None:
	"""
	Удаляет сообщения с определенными callback_data паттернами
	
	Args:
		message: Сообщение, от которого нужно очистить чат
		callback_data_patterns: Список паттернов callback_data для удаления
		max_messages: Максимальное количество сообщений для проверки
	"""
	try:
		chat_id = message.chat.id
		user_id = message.from_user.id
		
		async for msg in message.bot.get_chat_history(chat_id, limit=max_messages):
			# Пропускаем сообщения других пользователей
			if msg.from_user.id != user_id:
				continue
			
			# Проверяем callback_data в кнопках
			if msg.reply_markup:
				for row in msg.reply_markup.inline_keyboard:
					for button in row:
						if button.callback_data:
							for pattern in callback_data_patterns:
								if button.callback_data.startswith(pattern):
									try:
										await msg.delete()
										await asyncio.sleep(0.1)
										break
									except Exception:
										pass
									break
					else:
						continue
					break
					
	except Exception as e:
		print(f"Error cleaning up specific messages: {e}")


async def cleanup_workout_messages(message: types.Message) -> None:
	"""
	Очищает сообщения тренировок, но сохраняет текущее состояние
	"""
	exclude_patterns = [
		"workout_type:",
		"split:",
		"muscle_group:",
		"generate_",
		"show_exercise_videos:"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=30,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_cabinet_messages(message: types.Message) -> None:
	"""
	Очищает сообщения личного кабинета
	"""
	exclude_patterns = [
		"cabinet_",
		"set_new_goal",
		"upload_progress_photo",
		"view_progress_stats"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=30,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_payment_messages(message: types.Message) -> None:
	"""
	Очищает сообщения платежей
	"""
	exclude_patterns = [
		"pay_",
		"process_payment:",
		"check_payment:",
		"cancel_payment"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=20,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_menu_messages(message: types.Message) -> None:
	"""
	Очищает сообщения меню
	"""
	exclude_patterns = [
		"view_weekly_menu",
		"download_menu_pdf",
		"personal_nutrition",
		"search_meals"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=25,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_rewards_messages(message: types.Message) -> None:
	"""
	Очищает сообщения системы наград
	"""
	exclude_patterns = [
		"available_prizes",
		"exchange_stars",
		"stars_history",
		"invite_friend"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=25,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_settings_messages(message: types.Message) -> None:
	"""
	Очищает сообщения настроек
	"""
	exclude_patterns = [
		"toggle_notifications",
		"edit_profile",
		"edit_goals"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=20,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_stats_messages(message: types.Message) -> None:
	"""
	Очищает сообщения статистики
	"""
	exclude_patterns = [
		"workout_stats",
		"nutrition_stats",
		"progress_stats"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=20,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_referral_messages(message: types.Message) -> None:
	"""
	Очищает сообщения реферальной системы
	"""
	exclude_patterns = [
		"share_referral_link",
		"referral_stats"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=15,
		exclude_callback_data=exclude_patterns
	)


async def cleanup_support_messages(message: types.Message) -> None:
	"""
	Очищает сообщения поддержки
	"""
	exclude_patterns = [
		"write_to_support",
		"faq",
		"upgrade_to_pro"
	]
	
	await cleanup_old_messages(
		message, 
		keep_pinned=True, 
		max_messages=15,
		exclude_callback_data=exclude_patterns
	)