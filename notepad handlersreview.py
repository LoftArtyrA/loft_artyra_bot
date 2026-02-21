from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

async def reviews_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("⭐ Отзывы в разработке")
    await callback.answer()

def register_review_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(reviews_menu, lambda c: c.data == "reviews")