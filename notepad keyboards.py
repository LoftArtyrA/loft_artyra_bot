from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard():
    """Главное меню"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🛏️ Заказать кровать", callback_data="order_bed"),
        InlineKeyboardButton("🎯 Подобрать кровать (квиз)", callback_data="start_quiz"),
        InlineKeyboardButton("🎁 Реферальная программа", callback_data="referral"),
        InlineKeyboardButton("⭐ Отзывы", callback_data="reviews"),
        InlineKeyboardButton("🏭 Тур по производству", callback_data="tour"),
        InlineKeyboardButton("👨‍🎨 О мастере", callback_data="about_master"),
        InlineKeyboardButton("📞 Связаться", callback_data="contact_master")
    )
    return kb


def back_to_start_keyboard():
    """Кнопка возврата в главное меню"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    return kb


def admin_keyboard():
    """Админ-панель"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("🏠 В главное меню", callback_data="start_over")
    )
    return kb