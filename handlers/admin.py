from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import (
    get_all_orders, get_order_by_id, update_order_status,
    get_stats, get_all_users_for_broadcast
)
from keyboards import admin_keyboard
from config import ADMIN_TELEGRAM_ID
import asyncio
import re
from datetime import datetime

class BroadcastState(StatesGroup):
    waiting_for_message = State()

# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПРОВЕРКИ АДМИНА ==========

async def check_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    return user_id == ADMIN_TELEGRAM_ID

# ========== АДМИН-ПАНЕЛЬ ==========

async def admin_panel(message: types.Message):
    """Вход в админ-панель"""
    if not await check_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен")
        return
    
    await message.answer(
        "🔐 <b>АДМИН-ПАНЕЛЬ</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard()
    )

async def admin_stats_callback(callback: types.CallbackQuery):
    """Просмотр статистики"""
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return
    
    stats = get_stats()
    total_sum = f"{stats['total_sum']:,}".replace(',', ' ')
    paid_sum = f"{stats['paid_sum']:,}".replace(',', ' ')
    
    text = (
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"👥 <b>Пользователи:</b> {stats['total_users']}\n"
        f"📦 <b>Всего заказов:</b> {stats['total_orders']}\n"
        f"✅ <b>Завершено:</b> {stats['completed_orders']}\n"
        f"⏳ <b>В обработке:</b> {stats['pending_orders']}\n"
        f"💰 <b>Оплачено:</b> {stats['paid_orders']}\n"
        f"💵 <b>Общая сумма:</b> {total_sum} ₽\n"
        f"💳 <b>Получено:</b> {paid_sum} ₽\n"
        f"⭐ <b>Средний рейтинг:</b> {stats['avg_rating']}\n"
        f"📝 <b>Отзывов:</b> {stats['total_reviews']}"
    )
    
    await callback.message.edit_text(text, reply_markup=admin_keyboard())
    await callback.answer()

async def admin_orders_callback(callback: types.CallbackQuery):
    """Просмотр всех заказов"""
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return
    
    orders = get_all_orders()
    
    if not orders:
        await callback.message.edit_text(
            "📦 Заказов пока нет",
            reply_markup=admin_keyboard()
        )
        await callback.answer()
        return
    
    text = "📦 <b>ВСЕ ЗАКАЗЫ</b>\n\n"
    for order in orders[:10]:
        status_emoji = {
            'pending': '⏳',
            'paid': '💰',
            'receipt_uploaded': '📎',
            'confirmed': '✅',
            'completed': '🎉'
        }.get(order['status'], '⏳')
        
        username = order['username'] if order['username'] else 'нет'
        text += (
            f"{status_emoji} <b>Заказ #{order['id']}</b>\n"
            f"👤 {username}\n"
            f"💰 {order['total']} ₽\n"
            f"📅 {order['created_at'][:10]}\n"
            f"Статус: {order['status']}\n"
            f"🔍 /order_{order['id']}\n\n"
        )
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔄 Обновить", callback_data="admin_orders"),
        types.InlineKeyboardButton("🏠 Назад", callback_data="admin_back")
    )
    
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

# ========== РАССЫЛКА ==========

async def admin_broadcast_callback(callback: types.CallbackQuery, state: FSMContext):
    """Начать рассылку"""
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return
    
    await BroadcastState.waiting_for_message.set()
    await callback.message.edit_text(
        "📢 <b>РАССЫЛКА</b>\n\n"
        "Введите текст сообщения для рассылки всем пользователям:\n"
        "(можно использовать HTML-разметку)",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("❌ Отмена", callback_data="admin_back")
        )
    )
    await callback.answer()

async def broadcast_message(message: types.Message, state: FSMContext):
    """Отправка рассылки"""
    if not await check_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен")
        await state.finish()
        return
    
    users = get_all_users_for_broadcast()
    text = message.html_text
    
    if not users:
        await message.answer("❌ Нет пользователей для рассылки")
        await state.finish()
        return
    
    status_msg = await message.answer(f"📢 Начинаю рассылку {len(users)} пользователям...")
    
    success = 0
    failed = 0
    
    for i, user_id in enumerate(users):
        try:
            await message.bot.send_message(user_id, text)
            success += 1
        except Exception as e:
            failed += 1
            print(f"Ошибка отправки пользователю {user_id}: {e}")
        
        if i % 10 == 0:
            try:
                await status_msg.edit_text(f"📢 Прогресс: {i}/{len(users)} (✅ {success} | ❌ {failed})")
            except:
                pass
        
        await asyncio.sleep(0.05)
    
    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена</b>\n\n"
        f"📊 Всего пользователей: {len(users)}\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed}"
    )
    
    await state.finish()

# ========== ОБРАБОТЧИКИ ДЛЯ ЧЕКОВ ==========

async def confirm_payment_handler(callback: types.CallbackQuery):
    """ПОДТВЕРЖДЕНИЕ ОПЛАТЫ ПО ЧЕКУ"""
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return
    
    try:
        callback_data = callback.data
        print(f"✅ НАЖАТА КНОПКА ПОДТВЕРЖДЕНИЯ: {callback_data}")
        
        numbers = re.findall(r'\d+', callback_data)
        if not numbers:
            await callback.answer("❌ Не удалось определить номер заказа", show_alert=True)
            return
        
        order_id = int(numbers[-1])
        print(f"📦 ПОДТВЕРЖДАЕМ ЗАКАЗ #{order_id}")
        
        update_order_status(order_id, 'confirmed')
        print(f"✅ СТАТУС ЗАКАЗА #{order_id} ИЗМЕНЕН НА 'confirmed'")
        
        order = get_order_by_id(order_id)
        if order:
            try:
                await callback.bot.send_message(
                    order['user_id'],
                    f"✅ <b>Оплата подтверждена!</b>\n\n"
                    f"Ваш заказ #{order_id} передан в производство.\n"
                    f"🛏️ Срок изготовления: 10-14 дней"
                )
                print(f"👤 КЛИЕНТ {order['user_id']} УВЕДОМЛЕН")
            except Exception as e:
                print(f"❌ Ошибка уведомления клиента: {e}")
        
        await callback.answer("✅ Подтверждено!")
        
        try:
            if callback.message.caption:
                new_caption = callback.message.caption + "\n\n✅ <b>ПОДТВЕРЖДЕНО</b>"
                await callback.message.edit_caption(new_caption)
                await callback.message.edit_reply_markup(reply_markup=None)
            else:
                await callback.message.edit_text(
                    callback.message.text + "\n\n✅ <b>ПОДТВЕРЖДЕНО</b>",
                    reply_markup=None
                )
        except Exception as e:
            print(f"⚠️ Не удалось обновить сообщение: {e}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        await callback.answer(f"❌ Ошибка", show_alert=True)

async def reject_payment_handler(callback: types.CallbackQuery):
    """ОТКЛОНЕНИЕ ЧЕКА"""
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return
    
    try:
        callback_data = callback.data
        print(f"❌ НАЖАТА КНОПКА ОТКЛОНЕНИЯ: {callback_data}")
        
        numbers = re.findall(r'\d+', callback_data)
        if not numbers:
            await callback.answer("❌ Не удалось определить номер заказа", show_alert=True)
            return
        
        order_id = int(numbers[-1])
        print(f"📦 ОТКЛОНЯЕМ ЧЕК ЗАКАЗА #{order_id}")
        
        update_order_status(order_id, 'paid')
        print(f"✅ СТАТУС ЗАКАЗА #{order_id} ИЗМЕНЕН НА 'paid'")
        
        order = get_order_by_id(order_id)
        if order:
            try:
                await callback.bot.send_message(
                    order['user_id'],
                    f"❌ <b>Чек не прошел проверку</b>\n\n"
                    f"Пожалуйста, загрузите четкое фото чека об оплате."
                )
                print(f"👤 КЛИЕНТ {order['user_id']} УВЕДОМЛЕН")
            except Exception as e:
                print(f"❌ Ошибка уведомления клиента: {e}")
        
        await callback.answer("❌ Отклонено!")
        
        try:
            if callback.message.caption:
                new_caption = callback.message.caption + "\n\n❌ <b>ОТКЛОНЕНО</b>"
                await callback.message.edit_caption(new_caption)
                await callback.message.edit_reply_markup(reply_markup=None)
            else:
                await callback.message.edit_text(
                    callback.message.text + "\n\n❌ <b>ОТКЛОНЕНО</b>",
                    reply_markup=None
                )
        except Exception as e:
            print(f"⚠️ Не удалось обновить сообщение: {e}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        await callback.answer(f"❌ Ошибка", show_alert=True)

# ========== НАВИГАЦИЯ ==========

async def admin_back_callback(callback: types.CallbackQuery):
    """Возврат в админ-панель"""
    if not await check_admin(callback.from_user.id):
        await callback.answer("⛔ Доступ запрещен", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔐 <b>АДМИН-ПАНЕЛЬ</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard()
    )
    await callback.answer()

# ========== СТАТИСТИКА ==========

async def cmd_stats(message: types.Message):
    """Показать статистику бота (команда /stats)"""
    if not await check_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен")
        return
    
    try:
        from stats import get_stats
        
        stats = get_stats()
        
        text = (
            f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
            f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
            f"📦 Всего заказов: <b>{stats['total_orders']}</b>\n"
            f"💰 Оплаченных заказов: <b>{stats['paid_orders']}</b>\n"
            f"🟢 Активных за 24ч: <b>{stats['active_24h']}</b>\n"
            f"📈 Активных за 7 дней: <b>{stats['active_7d']}</b>\n\n"
            f"<i>Данные на {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"
        )
        
        await message.answer(text, reply_markup=admin_keyboard())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка получения статистики: {e}")

# ========== РЕГИСТРАЦИЯ ВСЕХ ОБРАБОТЧИКОВ ==========

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'])
    dp.register_message_handler(cmd_stats, commands=['stats'])
    dp.register_callback_query_handler(admin_stats_callback, lambda c: c.data == "admin_stats")
    dp.register_callback_query_handler(admin_orders_callback, lambda c: c.data == "admin_orders")
    dp.register_callback_query_handler(admin_broadcast_callback, lambda c: c.data == "admin_broadcast")
    dp.register_callback_query_handler(admin_back_callback, lambda c: c.data == "admin_back")
    dp.register_message_handler(broadcast_message, state=BroadcastState.waiting_for_message)
    
    # Обработчики для чеков
    dp.register_callback_query_handler(confirm_payment_handler, lambda c: 'confirm' in c.data.lower())
    dp.register_callback_query_handler(reject_payment_handler, lambda c: 'reject' in c.data.lower())