from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("test"))
async def test_command(message: types.Message):
    """Тестовая команда"""
    text = "🧪 <b>Тест кнопок</b>\n\nНажмите на кнопку ниже:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Тестовая кнопка", callback_data="test_button")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "test_button")
async def test_button_handler(callback: types.CallbackQuery):
    """Обработчик тестовой кнопки"""
    print(f"✅ Получен тестовый callback: {callback.data} от пользователя {callback.from_user.id}")
    await callback.answer("✅ Кнопка работает!")
    await callback.message.edit_text(
        "✅ <b>Тест успешен!</b>\n\nКнопки работают корректно.",
        parse_mode="HTML"
    )