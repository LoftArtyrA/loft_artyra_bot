from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

async def start_tour(callback: types.CallbackQuery):
    await callback.message.edit_text("🏭 Тур по производству в разработке")
    await callback.answer()

def register_tour_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_tour, lambda c: c.data == "tour")