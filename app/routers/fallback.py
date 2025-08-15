from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query()
async def handle_all_callbacks(callback: types.CallbackQuery):
    """Обработчик всех необработанных callback_query"""
    try:
        print(f"🔍 Необработанный callback: {callback.data} от пользователя {callback.from_user.id}")
        await callback.answer(f"Обрабатывается: {callback.data}")
        
        # Показываем информацию о callback
        text = f"🔍 <b>Отладочная информация</b>\n\n"
        text += f"Callback data: <code>{callback.data}</code>\n"
        text += f"User ID: <code>{callback.from_user.id}</code>\n"
        text += f"Message ID: <code>{callback.message.message_id}</code>\n\n"
        text += "Этот callback не был обработан ни одним из роутеров."
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Начать заново", callback_data="start")]
        ])
        
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        
    except Exception as e:
        print(f"❌ Ошибка в fallback обработчике: {e}")
        await callback.answer(f"Ошибка: {str(e)}")

@router.callback_query(lambda c: c.data == "start")
async def start_callback(callback: types.CallbackQuery):
    """Обработка кнопки start"""
    try:
        from app.routers.start import on_start
        await on_start(callback.message)
        await callback.answer("✅ Переход на главную страницу")
    except Exception as e:
        print(f"❌ Ошибка в start callback: {e}")
        await callback.answer(f"Ошибка: {str(e)}")

@router.message()
async def handle_all_messages(message: types.Message):
    """Обработчик всех необработанных сообщений"""
    if message.text and not message.text.startswith('/'):
        await message.answer("🤖 Я не понимаю эту команду. Используйте /start для начала работы.")