#!/usr/bin/env python3
"""
Роутер для управления обновлениями контента
"""

from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.config import settings
from app.services.content_updater import content_updater
import os

router = Router()


class ContentManagementStates(StatesGroup):
    waiting_for_workouts_file = State()
    waiting_for_nutrition_file = State()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id in settings.admin_ids_list


@router.message(Command("content"))
async def content_management_command(message: types.Message):
    """Команда управления контентом"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    text = (
        "🔄 <b>Управление контентом</b>\n\n"
        "Выберите действие:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика контента", callback_data="content_stats")],
        [InlineKeyboardButton(text="🔄 Обновить тренировки", callback_data="update_workouts")],
        [InlineKeyboardButton(text="🍽️ Обновить питание", callback_data="update_nutrition")],
        [InlineKeyboardButton(text="📝 Создать примеры JSON", callback_data="create_samples")],
        [InlineKeyboardButton(text="📁 Проверить файлы", callback_data="check_files")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(lambda c: c.data == "content_stats")
async def show_content_stats(callback: types.CallbackQuery):
    """Показать статистику контента"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    try:
        stats = await content_updater.get_content_stats()
        
        if "error" in stats:
            text = f"❌ Ошибка получения статистики: {stats['error']}"
        else:
            text = "📊 <b>Статистика контента</b>\n\n"
            
            # Статистика упражнений
            text += "🏋️‍♂️ <b>Упражнения:</b>\n"
            for muscle_group, level, count in stats["exercises"]:
                text += f"  • {muscle_group} ({level}): {count}\n"
            
            text += f"\n🍽️ <b>Блюда:</b> {stats['meals_count']}\n"
            text += f"📋 <b>Программы:</b> {stats['programs_count']}\n"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="content_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(lambda c: c.data == "update_workouts")
async def update_workouts_handler(callback: types.CallbackQuery):
    """Обновить тренировки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    try:
        await callback.answer("🔄 Обновление тренировок...")
        
        result = await content_updater.update_workouts_from_json()
        
        if result["success"]:
            text = f"✅ <b>Обновление тренировок завершено</b>\n\n{result['message']}\n\n"
            if result["errors"]:
                text += f"⚠️ Ошибки: {len(result['errors'])}\n"
            text += f"📁 Архивировано: {result['archived']}"
        else:
            text = f"❌ <b>Ошибка обновления</b>\n\n{result['message']}"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="content_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(lambda c: c.data == "update_nutrition")
async def update_nutrition_handler(callback: types.CallbackQuery):
    """Обновить питание"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    try:
        await callback.answer("🔄 Обновление питания...")
        
        result = await content_updater.update_nutrition_from_json()
        
        if result["success"]:
            text = f"✅ <b>Обновление питания завершено</b>\n\n{result['message']}\n\n"
            if result["errors"]:
                text += f"⚠️ Ошибки: {len(result['errors'])}\n"
            text += f"📁 Архивировано: {result['archived']}"
        else:
            text = f"❌ <b>Ошибка обновления</b>\n\n{result['message']}"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="content_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(lambda c: c.data == "create_samples")
async def create_sample_files(callback: types.CallbackQuery):
    """Создать примеры JSON файлов"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    try:
        await callback.answer("📝 Создание примеров...")
        
        workouts_file = content_updater.create_sample_workouts_json()
        nutrition_file = content_updater.create_sample_nutrition_json()
        
        text = (
            "✅ <b>Примеры JSON файлов созданы</b>\n\n"
            f"🏋️‍♂️ Тренировки: <code>{workouts_file}</code>\n"
            f"🍽️ Питание: <code>{nutrition_file}</code>\n\n"
            "Заполните эти файлы своими данными и переименуйте в:\n"
            "• <code>new_workouts.json</code>\n"
            "• <code>new_nutrition.json</code>\n\n"
            "Затем используйте кнопки обновления для автоматической загрузки."
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="content_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(lambda c: c.data == "check_files")
async def check_files_handler(callback: types.CallbackQuery):
    """Проверить наличие файлов"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    try:
        await callback.answer("📁 Проверка файлов...")
        
        workouts_exists = os.path.exists("new_workouts.json")
        nutrition_exists = os.path.exists("new_nutrition.json")
        
        text = "📁 <b>Проверка файлов</b>\n\n"
        
        if workouts_exists:
            size = os.path.getsize("new_workouts.json")
            text += f"✅ <code>new_workouts.json</code> ({size} байт)\n"
        else:
            text += "❌ <code>new_workouts.json</code> не найден\n"
        
        if nutrition_exists:
            size = os.path.getsize("new_nutrition.json")
            text += f"✅ <code>new_nutrition.json</code> ({size} байт)\n"
        else:
            text += "❌ <code>new_nutrition.json</code> не найден\n"
        
        text += "\n💡 Используйте 'Создать примеры JSON' для создания шаблонов."
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="content_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(lambda c: c.data == "content_back")
async def content_back_handler(callback: types.CallbackQuery):
    """Возврат к главному меню управления контентом"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    text = (
        "🔄 <b>Управление контентом</b>\n\n"
        "Выберите действие:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика контента", callback_data="content_stats")],
        [InlineKeyboardButton(text="🔄 Обновить тренировки", callback_data="update_workouts")],
        [InlineKeyboardButton(text="🍽️ Обновить питание", callback_data="update_nutrition")],
        [InlineKeyboardButton(text="📝 Создать примеры JSON", callback_data="create_samples")],
        [InlineKeyboardButton(text="📁 Проверить файлы", callback_data="check_files")]
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()