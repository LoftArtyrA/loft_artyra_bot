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
        InlineKeyboardButton("📞 Связаться", callback_data="contact_master"),
        InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"),
        InlineKeyboardButton("🔄 /start", callback_data="cmd_start")
    )
    return kb

def back_to_start_keyboard():
    """Кнопка возврата в главное меню"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def back_keyboard(back_callback: str = "back"):
    """Кнопки Назад и В начало"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data=back_callback))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def size_keyboard():
    """Выбор размера кровати"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📏 140x200 (41 000₽)", callback_data="size_140x200"),
        InlineKeyboardButton("📏 160x200 (44 000₽)", callback_data="size_160x200"),
        InlineKeyboardButton("📏 180x200 (48 000₽)", callback_data="size_180x200"),
        InlineKeyboardButton("📏 200x200 (53 000₽)", callback_data="size_200x200"),
        InlineKeyboardButton("📐 Нестандартный размер", callback_data="size_custom")
    )
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def construction_keyboard():
    """Выбор типа конструкции"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🧱 Крепление к стене (макс. надежность)", callback_data="const_wall"),
        InlineKeyboardButton("🦶 На 5 ножках (мобильность, эффект парения)", callback_data="const_legs")
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_size"))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def mattress_category_keyboard():
    """Выбор категории матраса"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💰 Бюджетная (от 4820₽)", callback_data="mattress_cat_budget"),
        InlineKeyboardButton("💎 Средняя (от 10120₽)", callback_data="mattress_cat_mid"),
        InlineKeyboardButton("👑 Премиум (от 20994₽)", callback_data="mattress_cat_premium"),
        InlineKeyboardButton("❌ Без матраса", callback_data="mattress_none")
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_construction"))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def mattress_keyboard(category):
    """Выбор матраса по категории"""
    kb = InlineKeyboardMarkup(row_width=1)
    
    mattresses = {
        "budget": [
            ("Стандарт 1", 4820),
            ("Стандарт 2", 5140),
            ("Стандарт 3", 5850)
        ],
        "mid": [
            ("Стандарт Струто", 10120),
            ("Sonis Soft", 11336),
            ("Flex 4", 13630),
            ("Уют Эконом", 14780)
        ],
        "premium": [
            ("Мультипак Paradise", 20994),
            ("Мультипак Relax", 21530),
            ("Lovely Люкс", 24710),
            ("Мультипак Престиж", 29512)
        ]
    }
    
    for name, price in mattresses.get(category, []):
        kb.add(InlineKeyboardButton(
            f"{name} — {price}₽",
            callback_data=f"mattress_{name}"
        ))
    
    kb.add(InlineKeyboardButton("🔙 К категориям", callback_data="back_to_categories"))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def partner_choice_keyboard():
    """Выбор магазина ткани"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🏬 Vip Textile (сайт)", callback_data="partner_vip"),
        InlineKeyboardButton("🏬 МеКом (сайт)", callback_data="partner_mekom"),
        InlineKeyboardButton("✏️ Ввести вручную", callback_data="partner_manual")
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_mattress"))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def ral_keyboard():
    """Выбор цвета RAL - С КОНКРЕТИКОЙ"""
    kb = InlineKeyboardMarkup(row_width=2)
    colors = [
        ("RAL 9003", "Белый"),
        ("RAL 7016", "Антрацит"),
        ("RAL 1013", "Слоновая кость"),
        ("RAL 3005", "Вишня"),
        ("RAL 5005", "Синий"),
        ("RAL 6019", "Зеленый"),
        ("RAL 8004", "Коричневый"),
        ("RAL 9005", "Черный")
    ]
    for code, name in colors:
        kb.add(InlineKeyboardButton(f"{code} ({name})", callback_data=f"ral_{code}"))
    kb.add(InlineKeyboardButton("🎨 Другой цвет (вписать)", callback_data="ral_custom"))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_partner"))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def pillows_keyboard():
    """Выбор подушек"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Да, 2 шт (3000₽)", callback_data="pillows_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="pillows_no")
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_ral"))
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def confirm_keyboard():
    """Подтверждение заказа"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order"),
        InlineKeyboardButton("✏️ Изменить", callback_data="edit_order")
    )
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="start_over"))
    kb.add(InlineKeyboardButton("🔄 /start", callback_data="cmd_start"))
    return kb

def payment_keyboard():
    """Кнопки оплаты"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Я оплатил(а)", callback_data="paid"),
        InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"),
        InlineKeyboardButton("🔄 /start", callback_data="cmd_start")
    )
    return kb

def admin_keyboard():
    """Админ-панель"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("📦 Все заказы", callback_data="admin_orders"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("🏠 На главную", callback_data="start_over"),
        InlineKeyboardButton("🔄 /start", callback_data="cmd_start")
    )
    return kb