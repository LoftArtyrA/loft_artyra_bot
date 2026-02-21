from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🎯 Квиз в разработке")
    await callback.answer()

def register_quiz_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_quiz, lambda c: c.data == "start_quiz", state='*')