from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import PAYMENT_CARD, PAYMENT_RECEIVER, ADMIN_TELEGRAM_ID
from keyboards import (
    size_keyboard, construction_keyboard, mattress_category_keyboard,
    mattress_keyboard, ral_keyboard, pillows_keyboard,
    confirm_keyboard, payment_keyboard, back_keyboard, partner_choice_keyboard,
    start_keyboard
)
from data.prices import BED_PRICES, MATTRESSES
from utils.helpers import calculate_total, format_price


class OrderState(StatesGroup):
    size = State()
    construction = State()
    mattress_category = State()
    mattress = State()
    partner = State()
    fabric = State()
    ral = State()
    pillows = State()
    comment = State()
    confirmation = State()
    waiting_for_receipt = State()
    receipt_confirmation = State()

async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await OrderState.size.set()
    text = (
        "🛏️ <b>ОФОРМЛЕНИЕ ЗАКАЗА</b>\n\n"
        "Выберите размер спального места:"
    )
    await callback.message.edit_text(text, reply_markup=size_keyboard())
    await callback.answer()

async def process_size(callback: types.CallbackQuery, state: FSMContext):
    size = callback.data.replace('size_', '')
    await state.update_data(bed_size=size)
    await OrderState.construction.set()
    
    text = (
        f"✅ Размер: <b>{size}</b>\n\n"
        "🔧 <b>Выберите тип конструкции:</b>\n\n"
        "🧱 <b>Крепление к стене</b> - максимальная надежность\n"
        "🦶 <b>На 5 ножках</b> - мобильность, эффект парения"
    )
    await callback.message.edit_text(text, reply_markup=construction_keyboard())
    await callback.answer()

async def process_construction(callback: types.CallbackQuery, state: FSMContext):
    const = "Крепление к стене" if callback.data == "const_wall" else "На 5 ножках"
    await state.update_data(construction=const)
    await OrderState.mattress_category.set()
    
    text = f"✅ Конструкция: <b>{const}</b>\n\n💤 Выберите категорию матраса:"
    await callback.message.edit_text(text, reply_markup=mattress_category_keyboard())
    await callback.answer()

async def process_mattress_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.replace('mattress_cat_', '')
    await state.update_data(mattress_category=category)
    await OrderState.mattress.set()
    
    text = "Выберите модель матраса:"
    await callback.message.edit_text(text, reply_markup=mattress_keyboard(category))
    await callback.answer()

async def process_mattress(callback: types.CallbackQuery, state: FSMContext):
    mattress = callback.data.replace('mattress_', '')
    prices = {
        "Стандарт 1": 4820, "Стандарт 2": 5140, "Стандарт 3": 5850,
        "Стандарт Струто": 10120, "Sonis Soft": 11336, "Flex 4": 13630,
        "Уют Эконом": 14780, "Мультипак Paradise": 20994,
        "Мультипак Relax": 21530, "Lovely Люкс": 24710,
        "Мультипак Престиж": 29512
    }
    price = prices.get(mattress, 0)
    await state.update_data(mattress=mattress, mattress_price=price)
    await OrderState.partner.set()
    
    text = (
        f"✅ Матрас: <b>{mattress}</b> ({price}₽)\n\n"
        f"🏬 Выберите магазин ткани:"
    )
    await callback.message.edit_text(text, reply_markup=partner_choice_keyboard())
    await callback.answer()

async def process_mattress_none(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(mattress="Без матраса", mattress_price=0)
    await OrderState.partner.set()
    
    text = (
        "✅ Матрас: <b>не выбран</b>\n\n"
        "🏬 Выберите магазин ткани:"
    )
    await callback.message.edit_text(text, reply_markup=partner_choice_keyboard())
    await callback.answer()

async def process_partner(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.replace('partner_', '')
    
    if choice == "manual":
        await OrderState.fabric.set()
        await callback.message.edit_text(
            "✏️ Введите название ткани:",
            reply_markup=back_keyboard("back_to_mattress")
        )
    elif choice == "vip":
        await state.update_data(fabric_shop="Vip Textile")
        await callback.message.edit_text(
            "🔗 <b>Vip Textile</b>\nhttps://vip-textile.ru/catalog\n\n"
            "📞 <b>Контакты:</b>\n📍 ул. Солнечная, 5а\n☎️ +7 (8332) 77-87-53\n\n"
            "✅ После выбора ткани нажмите кнопку ниже:",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✏️ Ввести название ткани", callback_data="enter_fabric")
            )
        )
    elif choice == "mekom":
        await state.update_data(fabric_shop="МеКом")
        await callback.message.edit_text(
            "🔗 <b>МеКом</b>\nhttps://mekom.ru/catalog\n\n"
            "📞 <b>Контакты:</b>\n📍 ул. Карла Маркса, 4а\n☎️ +7 (8332) 58-68-10\n\n"
            "✅ После выбора ткани нажмите кнопку ниже:",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✏️ Ввести название ткани", callback_data="enter_fabric")
            )
        )
    await callback.answer()

async def enter_fabric(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.fabric.set()
    await callback.message.edit_text(
        "✏️ Введите название выбранной ткани:",
        reply_markup=back_keyboard("back_to_partner")
    )
    await callback.answer()

async def process_fabric(message: types.Message, state: FSMContext):
    await state.update_data(fabric_name=message.text)
    await OrderState.ral.set()
    
    await message.answer(
        "🎨 <b>ВЫБЕРИТЕ ЦВЕТ КАРКАСА RAL</b>\n\n"
        "Выберите цвет из списка или введите свой:",
        reply_markup=ral_keyboard()
    )

async def process_ral(callback: types.CallbackQuery, state: FSMContext):
    ral = callback.data.replace('ral_', '')
    
    if ral == "custom":
        await OrderState.ral.set()
        await callback.message.edit_text(
            "✏️ Введите номер или название цвета RAL:\n"
            "(например: RAL 9003, антрацит, белый и т.д.)",
            reply_markup=back_keyboard("back_to_partner")
        )
    else:
        ral_parts = ral.split(' ')
        if len(ral_parts) >= 2:
            ral_code = ral_parts[1] if len(ral_parts) > 1 else ral_parts[0]
            colors = {
                "9003": "Белый",
                "7016": "Антрацит",
                "1013": "Слоновая кость",
                "3005": "Вишня",
                "5005": "Синий",
                "6019": "Зеленый",
                "8004": "Коричневый",
                "9005": "Черный"
            }
            color_name = colors.get(ral_code, "")
            ral_display = f"RAL {ral_code} ({color_name})" if color_name else f"RAL {ral_code}"
        else:
            ral_display = ral
        
        await state.update_data(ral_color=ral_display)
        await OrderState.pillows.set()
        
        await callback.message.edit_text(
            f"✅ Выбран цвет: <b>{ral_display}</b>\n\n"
            f"🛏️ Добавить декоративные подушки? (2 шт — 3000₽)",
            reply_markup=pillows_keyboard()
        )
    await callback.answer()

async def process_custom_ral(message: types.Message, state: FSMContext):
    await state.update_data(ral_color=message.text)
    await OrderState.pillows.set()
    
    await message.answer(
        "🛏️ Добавить подушки? (2 шт — 3000₽)",
        reply_markup=pillows_keyboard()
    )

async def process_pillows(callback: types.CallbackQuery, state: FSMContext):
    pillows = "yes" if callback.data == "pillows_yes" else "no"
    await state.update_data(pillows=pillows)
    await OrderState.comment.set()
    
    await callback.message.edit_text(
        "📝 Добавьте комментарий к заказу (или напишите 'нет'):",
        reply_markup=back_keyboard("back_to_ral")
    )
    await callback.answer()

async def process_comment(message: types.Message, state: FSMContext):
    comment = "" if message.text.lower() == "нет" else message.text
    await state.update_data(comment=comment)
    
    data = await state.get_data()
    prices = calculate_total(data)
    await state.update_data(**prices)
    
    summary = (
        f"<b>🧾 ВАШ ЗАКАЗ</b>\n\n"
        f"🛏️ Размер: {data.get('bed_size')}\n"
        f"🔧 Конструкция: {data.get('construction')}\n"
        f"💤 Матрас: {data.get('mattress')}\n"
        f"🎨 Ткань: {data.get('fabric_name', '—')}\n"
        f"🎨 Цвет RAL: {data.get('ral_color', '—')}\n"
        f"🛏️ Подушки: {'Да' if data.get('pillows') == 'yes' else 'Нет'}\n"
        f"📝 Комментарий: {data.get('comment', '—')}\n\n"
        f"💰 <b>ИТОГО: {prices['total']} ₽</b>\n"
        f"💳 <b>Предоплата: {prices['prepayment']} ₽</b>"
    )
    
    await OrderState.confirmation.set()
    await message.answer(summary, reply_markup=confirm_keyboard())

async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    from database import save_order
    order_id = save_order(
        callback.from_user.id,
        callback.from_user.username,
        callback.from_user.full_name,
        data
    )
    
    prepayment = data.get('prepayment', 0)
    
    text = (
        f"✅ <b>ЗАКАЗ #{order_id} ОФОРМЛЕН!</b>\n\n"
        f"Для запуска производства внесите предоплату:\n\n"
        f"💰 <b>{prepayment} ₽</b>\n\n"
        f"💳 Карта: <code>{PAYMENT_CARD}</code>\n"
        f"👤 Получатель: {PAYMENT_RECEIVER}\n\n"
        f"После оплаты нажмите кнопку ниже"
    )
    
    await callback.message.edit_text(text, reply_markup=payment_keyboard())
    await state.finish()
    await callback.answer()

async def process_paid(callback: types.CallbackQuery, state: FSMContext):
    try:
        import re
        match = re.search(r'#(\d+)', callback.message.text)
        if match:
            order_id = match.group(1)
        else:
            order_id = 'неизвестен'
        
        await state.update_data(pending_order_id=order_id)
        
        await callback.message.edit_text(
            f"✅ <b>Спасибо за оплату!</b>\n\n"
            f"📎 <b>Загрузите, пожалуйста, фото или скрин чека</b>\n\n"
            f"Это необходимо для подтверждения платежа.\n"
            f"После проверки мастер подтвердит заказ.",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("❌ Отмена", callback_data="start_over")
            )
        )
        
        await OrderState.waiting_for_receipt.set()
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

async def process_receipt(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            "❌ Пожалуйста, отправьте фото чека",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
            )
        )
        return
    
    data = await state.get_data()
    order_id = data.get('pending_order_id')
    
    if not order_id or order_id == 'неизвестен':
        await message.answer("❌ Ошибка: заказ не найден. Пожалуйста, начните заново.")
        await state.finish()
        return
    
    file_id = message.photo[-1].file_id
    await state.update_data(receipt_file_id=file_id)
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📤 Отправить чек", callback_data="send_receipt"),
        types.InlineKeyboardButton("🔄 Загрузить заново", callback_data="retry_receipt"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="start_over")
    )
    
    await message.answer_photo(
        photo=file_id,
        caption=f"📎 <b>Чек для заказа #{order_id}</b>\n\n"
                f"Проверьте, правильно ли загружен чек.\n"
                f"Если всё верно, нажмите кнопку 'Отправить'.",
        reply_markup=keyboard
    )
    
    await OrderState.receipt_confirmation.set()

async def send_receipt_callback(callback: types.CallbackQuery, state: FSMContext):
    """Отправка подтвержденного чека админу"""
    try:
        data = await state.get_data()
        order_id = data.get('pending_order_id')
        file_id = data.get('receipt_file_id')
        
        if not file_id or not order_id or order_id == 'неизвестен':
            await callback.message.edit_caption(
                caption="❌ Ошибка: данные чека не найдены",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
                )
            )
            await state.finish()
            return
        
        from database import update_order_receipt, get_order_by_id
        
        update_order_receipt(int(order_id), file_id)
        order = get_order_by_id(int(order_id))
        
        admin_text = (
            f"📎 <b>НОВЫЙ ЧЕК НА ПРОВЕРКУ!</b>\n\n"
            f"📦 Заказ #{order_id}\n"
            f"👤 Клиент: @{callback.from_user.username or 'нет'}\n"
            f"🆔 ID: {callback.from_user.id}\n"
            f"💰 Сумма предоплаты: {order['prepayment'] if order else '?'} ₽\n\n"
            f"<i>Проверьте чек и подтвердите оплату</i>"
        )
        
        await callback.bot.send_photo(
            ADMIN_TELEGRAM_ID,
            photo=file_id,
            caption=admin_text,
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{order_id}"),
                types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{order_id}")
            )
        )
        
        # ИСПРАВЛЕНО: Отправляем новое сообщение вместо редактирования
        await callback.message.delete()
        await callback.message.answer(
            "✅ <b>Чек отправлен!</b>\n\n"
            "Мастер проверит платеж и подтвердит заказ в ближайшее время.\n"
            "Мы уведомим вас, когда заказ будет передан в производство.",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
            )
        )
        
        await state.finish()
        await callback.answer("✅ Чек отправлен!")
        
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        await callback.message.answer(
            f"❌ Ошибка при отправке: {str(e)}",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
            )
        )
        await state.finish()
        await callback.answer("❌ Ошибка")

async def retry_receipt_callback(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.waiting_for_receipt.set()
    await callback.message.edit_caption(
        caption="📎 <b>Загрузите фото или скрин чека заново</b>",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("❌ Отмена", callback_data="start_over")
        )
    )
    await callback.answer()

# Обработчики для кнопок "Назад"
async def back_to_size(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.size.set()
    await callback.message.edit_text(
        "🛏️ <b>ОФОРМЛЕНИЕ ЗАКАЗА</b>\n\n"
        "Выберите размер спального места:",
        reply_markup=size_keyboard()
    )
    await callback.answer()

async def back_to_construction(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.construction.set()
    data = await state.get_data()
    size = data.get('bed_size', '')
    await callback.message.edit_text(
        f"✅ Размер: <b>{size}</b>\n\n"
        "🔧 <b>Выберите тип конструкции:</b>\n\n"
        "🧱 <b>Крепление к стене</b> - максимальная надежность\n"
        "🦶 <b>На 5 ножках</b> - мобильность, эффект парения",
        reply_markup=construction_keyboard()
    )
    await callback.answer()

async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.mattress_category.set()
    data = await state.get_data()
    const = data.get('construction', '')
    await callback.message.edit_text(
        f"✅ Конструкция: <b>{const}</b>\n\n💤 Выберите категорию матраса:",
        reply_markup=mattress_category_keyboard()
    )
    await callback.answer()

async def back_to_mattress(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.mattress.set()
    data = await state.get_data()
    category = data.get('mattress_category', 'mid')
    await callback.message.edit_text(
        "Выберите модель матраса:",
        reply_markup=mattress_keyboard(category)
    )
    await callback.answer()

async def back_to_partner(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.partner.set()
    await callback.message.edit_text(
        "🏬 Выберите магазин ткани:",
        reply_markup=partner_choice_keyboard()
    )
    await callback.answer()

async def back_to_ral(callback: types.CallbackQuery, state: FSMContext):
    await OrderState.ral.set()
    await callback.message.edit_text(
        "🎨 <b>ВЫБЕРИТЕ ЦВЕТ КАРКАСА RAL</b>\n\n"
        "Выберите цвет из списка или введите свой:",
        reply_markup=ral_keyboard()
    )
    await callback.answer()

def register_order_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_order, lambda c: c.data == "order_bed", state='*')
    dp.register_callback_query_handler(process_size, lambda c: c.data.startswith('size_'), state=OrderState.size)
    dp.register_callback_query_handler(process_construction, lambda c: c.data.startswith('const_'), state=OrderState.construction)
    dp.register_callback_query_handler(process_mattress_category, lambda c: c.data.startswith('mattress_cat_'), state=OrderState.mattress_category)
    dp.register_callback_query_handler(process_mattress, lambda c: c.data.startswith('mattress_'), state=OrderState.mattress)
    dp.register_callback_query_handler(process_mattress_none, lambda c: c.data == "mattress_none", state=OrderState.mattress_category)
    dp.register_callback_query_handler(process_partner, lambda c: c.data.startswith('partner_'), state=OrderState.partner)
    dp.register_callback_query_handler(enter_fabric, lambda c: c.data == "enter_fabric", state='*')
    dp.register_message_handler(process_fabric, state=OrderState.fabric)
    dp.register_callback_query_handler(process_ral, lambda c: c.data.startswith('ral_'), state=OrderState.ral)
    dp.register_message_handler(process_custom_ral, state=OrderState.ral)
    dp.register_callback_query_handler(process_pillows, lambda c: c.data.startswith('pillows_'), state=OrderState.pillows)
    dp.register_message_handler(process_comment, state=OrderState.comment)
    dp.register_callback_query_handler(confirm_order, lambda c: c.data == "confirm_order", state=OrderState.confirmation)
    dp.register_callback_query_handler(process_paid, lambda c: c.data == "paid", state='*')
    dp.register_message_handler(process_receipt, content_types=['photo'], state=OrderState.waiting_for_receipt)
    dp.register_callback_query_handler(send_receipt_callback, lambda c: c.data == "send_receipt", state=OrderState.receipt_confirmation)
    dp.register_callback_query_handler(retry_receipt_callback, lambda c: c.data == "retry_receipt", state=OrderState.receipt_confirmation)
    
    dp.register_callback_query_handler(back_to_size, lambda c: c.data == "back_to_size", state='*')
    dp.register_callback_query_handler(back_to_construction, lambda c: c.data == "back_to_construction", state='*')
    dp.register_callback_query_handler(back_to_categories, lambda c: c.data == "back_to_categories", state='*')
    dp.register_callback_query_handler(back_to_mattress, lambda c: c.data == "back_to_mattress", state='*')
    dp.register_callback_query_handler(back_to_partner, lambda c: c.data == "back_to_partner", state='*')
    dp.register_callback_query_handler(back_to_ral, lambda c: c.data == "back_to_ral", state='*')