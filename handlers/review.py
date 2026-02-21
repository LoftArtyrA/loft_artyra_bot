from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import save_review, get_approved_reviews, get_user_orders
from config import ADMIN_TELEGRAM_ID

class ReviewState(StatesGroup):
    rating = State()
    text = State()
    photo = State()

async def reviews_menu(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("⭐ Оставить отзыв", callback_data="write_review"),
        types.InlineKeyboardButton("👀 Посмотреть отзывы", callback_data="view_reviews"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
    )
    
    await callback.message.edit_text(
        "⭐ <b>ОТЗЫВЫ (в доработке)</b>\n\n"
        "Поделитесь впечатлениями или почитайте, что пишут другие!\n\n"
        "<i>⚙️ Функция находится в доработке</i>",
        reply_markup=kb
    )
    await callback.answer()

async def view_reviews(callback: types.CallbackQuery):
    reviews = get_approved_reviews(10)
    
    if not reviews:
        text = "⭐ Пока нет отзывов. Будьте первым!"
    else:
        text = "⭐ <b>ОТЗЫВЫ КЛИЕНТОВ</b>\n\n"
        for username, rating, review_text, photo, date in reviews:
            stars = "⭐" * rating + "☆" * (5 - rating)
            name = f"@{username}" if username else "Клиент"
            text += f"<b>{name}</b> {stars}\n"
            text += f"💬 {review_text}\n"
            text += "—" * 20 + "\n"
    
    from keyboards import back_to_start_keyboard
    await callback.message.edit_text(text, reply_markup=back_to_start_keyboard())
    await callback.answer()

async def write_review(callback: types.CallbackQuery, state: FSMContext):
    orders = get_user_orders(callback.from_user.id)
    
    if not orders:
        from keyboards import back_to_start_keyboard
        await callback.message.edit_text(
            "❌ Вы еще не делали заказов.\n"
            "Оставить отзыв можно только после получения заказа.",
            reply_markup=back_to_start_keyboard()
        )
        await callback.answer()
        return
    
    await ReviewState.rating.set()
    
    kb = types.InlineKeyboardMarkup(row_width=5)
    for i in range(1, 6):
        kb.insert(types.InlineKeyboardButton(f"{i}⭐", callback_data=f"rate_{i}"))
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"))
    
    await callback.message.edit_text(
        "⭐ <b>ОЦЕНИТЕ НАШУ РАБОТУ</b>\n\n"
        "От 1 до 5 звезд:",
        reply_markup=kb
    )
    await callback.answer()

async def process_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split('_')[1])
    await state.update_data(rating=rating)
    await ReviewState.text.set()
    
    from keyboards import back_to_start_keyboard
    await callback.message.edit_text(
        "📝 <b>НАПИШИТЕ ОТЗЫВ</b>\n\n"
        "Расскажите о вашем опыте:\n"
        "• Что понравилось?\n"
        "• Как кровать вписалась в интерьер?\n"
        "• Советуете ли друзьям?",
        reply_markup=back_to_start_keyboard()
    )
    await callback.answer()

async def process_review_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await ReviewState.photo.set()
    
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("📸 Добавить фото", callback_data="add_photo"),
        types.InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_photo"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
    )
    
    await message.answer(
        "📸 <b>ДОБАВЬТЕ ФОТО</b>\n\n"
        "Хотите прикрепить фото вашей кровати?",
        reply_markup=kb
    )

async def add_photo(callback: types.CallbackQuery, state: FSMContext):
    from keyboards import back_to_start_keyboard
    await callback.message.edit_text(
        "📸 Отправьте фото вашей кровати:",
        reply_markup=back_to_start_keyboard()
    )
    await callback.answer()

async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id if message.photo else None
    
    review_id = save_review(
        message.from_user.id,
        message.from_user.username,
        data['rating'],
        data['text'],
        photo_id
    )
    
    stars = "⭐" * data['rating']
    await message.bot.send_message(
        ADMIN_TELEGRAM_ID,
        f"🆕 <b>НОВЫЙ ОТЗЫВ</b>\n\n"
        f"👤 @{message.from_user.username}\n"
        f"⭐ {stars}\n"
        f"💬 {data['text']}\n\n"
        f"<i>Требуется модерация</i>"
    )
    
    from keyboards import back_to_start_keyboard
    await message.answer(
        "✅ <b>СПАСИБО ЗА ОТЗЫВ!</b>\n\n"
        "После модерации он появится в общем списке.",
        reply_markup=back_to_start_keyboard()
    )
    await state.finish()

async def skip_photo(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    review_id = save_review(
        callback.from_user.id,
        callback.from_user.username,
        data['rating'],
        data['text']
    )
    
    stars = "⭐" * data['rating']
    await callback.bot.send_message(
        ADMIN_TELEGRAM_ID,
        f"🆕 <b>НОВЫЙ ОТЗЫВ</b>\n\n"
        f"👤 @{callback.from_user.username}\n"
        f"⭐ {stars}\n"
        f"💬 {data['text']}\n\n"
        f"<i>Требуется модерация (без фото)</i>"
    )
    
    from keyboards import back_to_start_keyboard
    await callback.message.edit_text(
        "✅ <b>СПАСИБО ЗА ОТЗЫВ!</b>\n\n"
        "После модерации он появится в общем списке.",
        reply_markup=back_to_start_keyboard()
    )
    await state.finish()
    await callback.answer()

def register_review_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(reviews_menu, lambda c: c.data == "reviews")
    dp.register_callback_query_handler(view_reviews, lambda c: c.data == "view_reviews")
    dp.register_callback_query_handler(write_review, lambda c: c.data == "write_review")
    dp.register_callback_query_handler(process_rating, lambda c: c.data.startswith('rate_'), state=ReviewState.rating)
    dp.register_message_handler(process_review_text, state=ReviewState.text)
    dp.register_callback_query_handler(add_photo, lambda c: c.data == "add_photo", state=ReviewState.photo)
    dp.register_callback_query_handler(skip_photo, lambda c: c.data == "skip_photo", state=ReviewState.photo)
    dp.register_message_handler(process_photo, content_types=['photo'], state=ReviewState.photo)