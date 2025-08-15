from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy import select
from app.db.session import get_session_maker
from app.db.models import Purchase, User, ProgramLevel
from app.utils.chat_cleanup import cleanup_cabinet_messages

router = Router()


@router.message(Command("cabinet"))
async def cabinet(message: types.Message):
    await cleanup_cabinet_messages(message)
    await show_cabinet(message)


async def show_cabinet(message: types.Message):
    """Показать личный кабинет"""
    try:
        async_session = get_session_maker()
        async with async_session() as session:
            user = (await session.execute(select(User).where(User.tg_user_id == message.from_user.id))).scalar_one_or_none()
            paid = False
            level = None
            if user:
                p = (await session.execute(select(Purchase).where(Purchase.user_id == user.id, Purchase.paid == True))).first()
                paid = bool(p)
                level = user.level

        if not paid:
            await message.answer("❌ Доступ к личному кабинету открывается после оплаты.\n\nВыберите программу в /start")
            return

        level_text = f"Уровень: <b>{level.value.title()}</b>" if level else "Уровень не выбран"
        
        text = (
            f"🏠 <b>Личный кабинет</b>\n\n"
            f"{level_text}\n\n"
            "Выберите раздел:"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Цели и прогресс", callback_data="cabinet_goals")],
            [InlineKeyboardButton(text="🏋️‍♂️ Тренировки", callback_data="workouts")],
            [InlineKeyboardButton(text="🍲 Меню на неделю", callback_data="cabinet_menu")],
            [InlineKeyboardButton(text="🎁 Звезды и призы", callback_data="cabinet_rewards")],
            [InlineKeyboardButton(text="💬 Поддержка (PRO)", callback_data="cabinet_support")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="cabinet_settings")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="cabinet_stats")],
            [InlineKeyboardButton(text="🔗 Реферальная ссылка", callback_data="cabinet_referral")]
        ])

        await message.answer(text, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
        print(f"Error in show_cabinet: {e}")


@router.callback_query(lambda c: c.data == "cabinet")
async def cabinet_callback(callback: types.CallbackQuery):
    """Обработка кнопки личного кабинета"""
    print(f"🏠 Получен callback cabinet от пользователя {callback.from_user.id}")
    try:
        await cleanup_cabinet_messages(callback.message)
        await show_cabinet(callback.message)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_callback: {e}")


@router.callback_query(lambda c: c.data == "back_to_cabinet")
async def back_to_cabinet_callback(callback: types.CallbackQuery):
    """Возврат в личный кабинет"""
    print(f"🔙 Получен callback back_to_cabinet от пользователя {callback.from_user.id}")
    try:
        await cleanup_cabinet_messages(callback.message)
        await show_cabinet(callback.message)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in back_to_cabinet_callback: {e}")


@router.callback_query(lambda c: c.data == "cabinet_goals")
async def cabinet_goals(callback: types.CallbackQuery):
    """Цели и прогресс"""
    print(f"🎯 Получен callback cabinet_goals от пользователя {callback.from_user.id}")
    try:
        await cleanup_cabinet_messages(callback.message)
        
        async_session = get_session_maker()
        async with async_session() as session:
            user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
            
            if not user:
                await callback.answer("Пользователь не найден")
                return
            
            text = (
                f"🎯 <b>Цели и прогресс</b>\n\n"
                f"Текущий вес: <b>{user.weight_kg or 'Не указан'} кг</b>\n"
                f"Рост: <b>{user.height_cm or 'Не указан'} см</b>\n"
                f"Звезды: <b>{user.stars} ⭐</b>\n\n"
                "Выберите действие:"
            )
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Поставить новую цель", callback_data="set_new_goal")],
                [InlineKeyboardButton(text="📸 Загрузить фото прогресса", callback_data="upload_progress_photo")],
                [InlineKeyboardButton(text="📊 Посмотреть статистику", callback_data="view_progress_stats")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
            ])
            
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_goals: {e}")


@router.callback_query(lambda c: c.data == "cabinet_menu")
async def cabinet_menu(callback: types.CallbackQuery):
    """Меню на неделю"""
    print(f"🍲 Получен callback cabinet_menu от пользователя {callback.from_user.id}")
    try:
        await callback.answer("Переход к меню...")
        # Здесь будет переход к меню
        from app.routers.menu import show_menu_menu
        await show_menu_menu(callback.message)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_menu: {e}")


@router.callback_query(lambda c: c.data == "cabinet_rewards")
async def cabinet_rewards(callback: types.CallbackQuery):
    """Звезды и призы"""
    print(f"🎁 Получен callback cabinet_rewards от пользователя {callback.from_user.id}")
    try:
        await callback.answer("Переход к звездам...")
        # Здесь будет переход к звездам
        from app.routers.rewards import show_rewards_menu
        await show_rewards_menu(callback.message)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_rewards: {e}")


@router.callback_query(lambda c: c.data == "cabinet_support")
async def cabinet_support(callback: types.CallbackQuery):
    """Поддержка"""
    print(f"💬 Получен callback cabinet_support от пользователя {callback.from_user.id}")
    try:
        await callback.answer("Переход к поддержке...")
        # Здесь будет переход к поддержке
        from app.routers.support import show_support_menu
        await show_support_menu(callback.message)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_support: {e}")


@router.callback_query(lambda c: c.data == "cabinet_settings")
async def cabinet_settings(callback: types.CallbackQuery):
    """Настройки"""
    print(f"⚙️ Получен callback cabinet_settings от пользователя {callback.from_user.id}")
    try:
        await callback.answer("Переход к настройкам...")
        # Здесь будет переход к настройкам
        from app.routers.settings import show_settings_menu
        await show_settings_menu(callback.message)
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_settings: {e}")


@router.callback_query(lambda c: c.data == "cabinet_stats")
async def cabinet_stats(callback: types.CallbackQuery):
    """Статистика"""
    print(f"📊 Получен callback cabinet_stats от пользователя {callback.from_user.id}")
    try:
        async_session = get_session_maker()
        async with async_session() as session:
            user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
            
            if not user:
                await callback.answer("Пользователь не найден")
                return
            
            text = (
                f"📊 <b>Ваша статистика</b>\n\n"
                f"Звезды: <b>{user.stars} ⭐</b>\n"
                f"Дата регистрации: <b>{user.created_at.strftime('%d.%m.%Y')}</b>\n"
                f"Уровень: <b>{user.level.value.title() if user.level else 'Не выбран'}</b>\n"
                f"PRO поддержка: <b>{'Да' if user.has_pro_support else 'Нет'}</b>\n\n"
                "Продолжайте тренироваться для улучшения статистики!"
            )
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
            ])
            
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_stats: {e}")


@router.callback_query(lambda c: c.data == "cabinet_referral")
async def cabinet_referral(callback: types.CallbackQuery):
    """Реферальная ссылка"""
    print(f"🔗 Получен callback cabinet_referral от пользователя {callback.from_user.id}")
    try:
        async_session = get_session_maker()
        async with async_session() as session:
            user = (await session.execute(select(User).where(User.tg_user_id == callback.from_user.id))).scalar_one_or_none()
            
            if not user:
                await callback.answer("Пользователь не найден")
                return
            
            referral_link = f"https://t.me/{(await callback.bot.get_me()).username}?start=ref{user.id}"
            
            text = (
                f"🔗 <b>Ваша реферальная ссылка</b>\n\n"
                f"За каждого друга вы получите <b>100 звезд</b>!\n"
                f"Друг получит <b>скидку 10%</b> на программу.\n\n"
                f"Ваша ссылка:\n<code>{referral_link}</code>\n\n"
                "Поделитесь ссылкой с друзьями!"
            )
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=f"ref{user.id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="cabinet")]
            ])
            
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
        print(f"Error in cabinet_referral: {e}")