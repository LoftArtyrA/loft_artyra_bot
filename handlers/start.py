from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from keyboards import start_keyboard, back_to_start_keyboard
from database import save_user, activate_referral_code
from config import MASTER_TELEGRAM, MASTER_PHONE

async def cmd_start(message: types.Message, state: FSMContext):
    """Команда /start"""
    await state.finish()
    
    args = message.get_args()
    referred_by = None
    
    if args and args.startswith('ref'):
        try:
            referred_by = int(args[3:])
        except:
            pass
    
    save_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
        referred_by
    )
    
    if referred_by and referred_by != message.from_user.id:
        success, msg = activate_referral_code(message.from_user.id, f"LOFT{referred_by}")
        if success:
            await message.answer(msg)
    
    await message.answer(
        "👋 <b>Loft_ArtyrA</b> - мастерская авторской мебели\n\n"
        "🛏️ Парящие кровати в стиле лофт\n"
        "⚡ Ручная работа\n"
        "🌳 Натуральное дерево и металл\n\n"
        "Выберите действие:",
        reply_markup=start_keyboard()
    )

async def process_cmd_start(callback: types.CallbackQuery, state: FSMContext):
    """Обработка кнопки /start"""
    await cmd_start(callback.message, state)
    await callback.answer()

async def process_start_over(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.finish()
    
    # ИСПРАВЛЕНО: Проверяем, есть ли текст в сообщении
    try:
        # Пробуем отредактировать существующее сообщение
        await callback.message.edit_text(
            "👋 <b>Loft_ArtyrA</b> - мастерская авторской мебели\n\n"
            "Выберите действие:",
            reply_markup=start_keyboard()
        )
    except:
        # Если не получается отредактировать - отправляем новое
        await callback.message.delete()
        await callback.message.answer(
            "👋 <b>Loft_ArtyrA</b> - мастерская авторской мебели\n\n"
            "Выберите действие:",
            reply_markup=start_keyboard()
        )
    await callback.answer()

async def about_master(callback: types.CallbackQuery):
    """О мастере"""
    try:
        await callback.message.edit_text(
            "👨‍🎨 <b>О МАСТЕРСКОЙ</b>\n\n"
            "Loft_ArtyrA - это:\n"
            "• Авторская мебель в стиле лофт\n"
            "• Только натуральные материалы\n"
            "• Ручная работа с душой\n"
            "• Индивидуальный подход\n"
            "• Гарантия 2 года\n\n"
            "📍 Киров\n"
            "⏰ Пн-Пт 9:00-19:00, Сб 10:00-16:00",
            reply_markup=back_to_start_keyboard()
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            "👨‍🎨 <b>О МАСТЕРСКОЙ</b>\n\n"
            "Loft_ArtyrA - это:\n"
            "• Авторская мебель в стиле лофт\n"
            "• Только натуральные материалы\n"
            "• Ручная работа с душой\n"
            "• Индивидуальный подход\n"
            "• Гарантия 2 года\n\n"
            "📍 Киров\n"
            "⏰ Пн-Пт 9:00-19:00, Сб 10:00-16:00",
            reply_markup=back_to_start_keyboard()
        )
    await callback.answer()

async def contact_master(callback: types.CallbackQuery):
    """Контакты"""
    text = (
        "📞 <b>СВЯЗАТЬСЯ С МАСТЕРОМ</b>\n\n"
        f"📱 Telegram: {MASTER_TELEGRAM}\n"
        f"☎️ Телефон: {MASTER_PHONE}\n\n"
        "✏️ Просто напишите сюда - мастер ответит в ближайшее время!"
    )
    try:
        await callback.message.edit_text(text, reply_markup=back_to_start_keyboard())
    except:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=back_to_start_keyboard())
    await callback.answer()

def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'], state='*')
    dp.register_callback_query_handler(process_start_over, lambda c: c.data == "start_over", state='*')
    dp.register_callback_query_handler(process_cmd_start, lambda c: c.data == "cmd_start", state='*')
    dp.register_callback_query_handler(about_master, lambda c: c.data == "about_master")
    dp.register_callback_query_handler(contact_master, lambda c: c.data == "contact_master")