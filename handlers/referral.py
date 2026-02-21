from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_user, get_referrals_count

class ReferralState(StatesGroup):
    waiting_for_code = State()

async def referral_program(callback: types.CallbackQuery):
    """Реферальная программа (в доработке)"""
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ошибка загрузки данных")
        return
    
    bot = callback.bot
    bot_info = await bot.get_me()
    referrals_count = get_referrals_count(callback.from_user.id)
    
    text = (
        "🎁 <b>РЕФЕРАЛЬНАЯ ПРОГРАММА (в доработке)</b>\n\n"
        f"👤 Ваш код: <code>{user['referral_code']}</code>\n"
        f"👥 Приглашено друзей: {referrals_count}\n"
        f"💰 Бонусный баланс: {user['bonus_balance']}₽\n\n"
        "✨ <b>Как это будет работать:</b>\n"
        "• Вы даете другу свой код\n"
        "• Друг вводит код при старте\n"
        "• Вы получаете 1000₽ бонуса\n"
        "• Друг получает 500₽ скидку\n\n"
        "🔗 <b>Ваша ссылка:</b>\n"
        f"https://t.me/{bot_info.username}?start=ref{callback.from_user.id}\n\n"
        "<i>⚙️ Функция находится в доработке. Скоро будет полностью готова!</i>"
    )
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📤 Поделиться", switch_inline_query=f"Закажи кровать со скидкой 500₽! Мой код: {user['referral_code']}"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
    )
    
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

def register_referral_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(referral_program, lambda c: c.data == "referral")