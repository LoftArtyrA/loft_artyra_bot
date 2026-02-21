from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class OrderState(StatesGroup):
    waiting_for_size = State()

async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🛏️ Функция заказа в разработке")
    await callback.answer()

def register_order_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_order, lambda c: c.data == "order_bed", state='*')