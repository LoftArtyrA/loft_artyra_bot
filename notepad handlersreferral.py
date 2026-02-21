from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

async def referral_program(callback: types.CallbackQuery):
    await callback.message.edit_text("🎁 Реферальная программа в разработке")
    await callback.answer()

def register_referral_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(referral_program, lambda c: c.data == "referral")