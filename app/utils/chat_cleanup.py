import asyncio
from typing import Optional, List
from aiogram import types
from aiogram.exceptions import TelegramBadRequest


async def cleanup_old_messages(
    message: types.Message,
    keep_pinned: bool = True,
    max_messages: int = 50,
    exclude_callback_data: Optional[List[str]] = None
) -> None:
    """
    Удаляет старые сообщения в чате, оставляя закрепленные и исключая определенные callback_data
    """
    if exclude_callback_data is None:
        exclude_callback_data = []
    
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # Получаем историю сообщений
        async for msg in message.bot.get_chat_history(chat_id, limit=max_messages):
            # Пропускаем сообщения не от пользователя
            if msg.from_user.id != user_id:
                continue
            
            # Пропускаем закрепленные сообщения
            if keep_pinned and msg.is_automatic_forward:
                continue
            
            # Проверяем, есть ли кнопки с исключаемыми callback_data
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
            except TelegramBadRequest as e:
                if "message to delete not found" not in str(e).lower():
                    print(f"Error deleting message: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error deleting message: {e}")
                continue
                
    except Exception as e:
        print(f"Error in cleanup_old_messages: {e}")


async def cleanup_specific_messages(
    message: types.Message,
    callback_data_patterns: List[str],
    keep_pinned: bool = True
) -> None:
    """
    Удаляет сообщения с определенными callback_data паттернами
    """
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        async for msg in message.bot.get_chat_history(chat_id, limit=100):
            if msg.from_user.id != user_id:
                continue
            
            if keep_pinned and msg.is_automatic_forward:
                continue
            
            if msg.reply_markup:
                for row in msg.reply_markup.inline_keyboard:
                    for button in row:
                        if button.callback_data:
                            for pattern in callback_data_patterns:
                                if button.callback_data.startswith(pattern):
                                    try:
                                        await msg.delete()
                                        await asyncio.sleep(0.1)
                                    except TelegramBadRequest:
                                        pass
                                    except Exception as e:
                                        print(f"Error deleting message: {e}")
                                    break
                                    
    except Exception as e:
        print(f"Error in cleanup_specific_messages: {e}")


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
        "workouts",
        "menu",
        "rewards",
        "support",
        "settings",
        "stats",
        "referral"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=20,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_menu_messages(message: types.Message) -> None:
    """
    Очищает сообщения меню питания
    """
    exclude_patterns = [
        "menu_",
        "meal_",
        "nutrition_",
        "kbju_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=20,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_rewards_messages(message: types.Message) -> None:
    """
    Очищает сообщения системы наград
    """
    exclude_patterns = [
        "rewards_",
        "prize_",
        "stars_",
        "raffle_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=20,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_settings_messages(message: types.Message) -> None:
    """
    Очищает сообщения настроек
    """
    exclude_patterns = [
        "settings_",
        "profile_",
        "notifications_"
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
        "support_",
        "contact_",
        "help_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=15,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_instagram_messages(message: types.Message) -> None:
    """
    Очищает сообщения Instagram
    """
    exclude_patterns = [
        "instagram_",
        "challenge_",
        "post_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=15,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_ai_kbju_messages(message: types.Message) -> None:
    """
    Очищает сообщения AI КБЖУ
    """
    exclude_patterns = [
        "kbju_",
        "analyze_",
        "photo_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=15,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_referral_messages(message: types.Message) -> None:
    """
    Очищает сообщения реферальной системы
    """
    exclude_patterns = [
        "referral_",
        "ref_",
        "invite_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=15,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_purchase_messages(message: types.Message) -> None:
    """
    Очищает сообщения покупок
    """
    exclude_patterns = [
        "buy:",
        "pay_",
        "purchase_",
        "process_payment:"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=20,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_start_messages(message: types.Message) -> None:
    """
    Очищает сообщения стартового меню
    """
    exclude_patterns = [
        "choose_program",
        "buy:"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=10,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_all_except_workouts(message: types.Message) -> None:
    """
    Очищает все сообщения кроме тренировок
    """
    exclude_patterns = [
        "workout_",
        "exercise_",
        "muscle_",
        "split_",
        "generate_",
        "show_exercise_"
    ]
    
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=50,
        exclude_callback_data=exclude_patterns
    )


async def cleanup_general_messages(message: types.Message) -> None:
    """
    Общая очистка для всех остальных разделов
    """
    await cleanup_old_messages(
        message,
        keep_pinned=True,
        max_messages=30,
        exclude_callback_data=[]
    )