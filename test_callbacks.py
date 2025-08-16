#!/usr/bin/env python3
"""
Тест для проверки работы callback_query
"""

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Используем тестовый токен для проверки
TOKEN = "8269244638:AAHbZ8O3eJ6dt-SRmsdnP_bQ9XTn0zxScY"

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    @dp.message(Command("test"))
    async def test_command(message: types.Message):
        """Тестовая команда"""
        text = "🧪 <b>Тест кнопок</b>\n\nНажмите на кнопку ниже:"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔘 Тестовая кнопка", callback_data="test_button")]
        ])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")

    @dp.callback_query(lambda c: c.data == "test_button")
    async def test_button_handler(callback: types.CallbackQuery):
        """Обработчик тестовой кнопки"""
        print(f"✅ Получен callback: {callback.data}")
        await callback.answer("✅ Кнопка работает!")
        await callback.message.edit_text(
            "✅ <b>Тест успешен!</b>\n\nКнопки работают корректно.",
            parse_mode="HTML"
        )

    @dp.callback_query()
    async def handle_all_callbacks(callback: types.CallbackQuery):
        """Обработчик всех callback_query"""
        print(f"🔍 Необработанный callback: {callback.data}")
        await callback.answer(f"Получен: {callback.data}")

    print("🚀 Запуск тестового бота...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())