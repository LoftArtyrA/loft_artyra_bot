from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

class TourState(StatesGroup):
    in_progress = State()

# Этапы тура (без фото, только текст)
TOUR_STAGES = [
    {
        "title": "1️⃣ ПОДГОТОВКА МАТЕРИАЛОВ",
        "text": "Отбираем лучшее дерево — сосну, дуб или лиственницу. Металл — профильная труба высшего качества."
    },
    {
        "title": "2️⃣ РАСКРОЙ МАТЕРИАЛОВ",
        "text": "Точный раскрой по чертежам. Каждая деталь вымеряется с точностью до миллиметра."
    },
    {
        "title": "3️⃣ СВАРОЧНЫЕ РАБОТЫ",
        "text": "Создаём металлический каркас. Используем аргонную сварку для идеальных швов."
    },
    {
        "title": "4️⃣ ОБРАБОТКА ДЕРЕВА",
        "text": "Шлифовка в 3 этапа, пропитка маслом или воском, защитное покрытие."
    },
    {
        "title": "5️⃣ ПОКРАСКА КАРКАСА",
        "text": "Порошковая покраска в цвет RAL. Устойчива к царапинам и выцветанию."
    },
    {
        "title": "6️⃣ ОБИВКА ИЗГОЛОВЬЯ",
        "text": "Обтягиваем изголовье выбранной тканью. Используем качественный поролон."
    },
    {
        "title": "7️⃣ ФИНАЛЬНАЯ СБОРКА",
        "text": "Собираем все элементы воедино. Проверяем надёжность креплений."
    },
    {
        "title": "8️⃣ КОНТРОЛЬ КАЧЕСТВА",
        "text": "Проверяем каждую деталь. Тестируем на прочность. Фотографируем готовое изделие."
    }
]

async def start_tour(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("▶️ НАЧАТЬ ТУР", callback_data="tour_begin"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
    )
    
    await callback.message.edit_text(
        "🏭 <b>ВИРТУАЛЬНЫЙ ТУР ПО ПРОИЗВОДСТВУ (в доработке)</b>\n\n"
        "Сейчас я покажу, как создаётся ваша кровать!\n"
        "Весь процесс от заготовки до готового изделия.\n\n"
        "<i>⚙️ Функция находится в доработке</i>",
        reply_markup=kb
    )
    await callback.answer()

async def begin_tour(callback: types.CallbackQuery, state: FSMContext):
    await TourState.in_progress.set()
    await callback.message.delete()
    
    for i, stage in enumerate(TOUR_STAGES):
        # Создаем клавиатуру
        kb = types.InlineKeyboardMarkup()
        
        # Для последнего этапа добавляем кнопку заказа
        if i == len(TOUR_STAGES) - 1:
            kb.add(
                types.InlineKeyboardButton("🛏️ ЗАКАЗАТЬ КРОВАТЬ", callback_data="order_bed"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
            )
        else:
            kb.add(types.InlineKeyboardButton("⏭️ ДАЛЕЕ", callback_data="tour_next"))
        
        # Отправляем текстовое сообщение вместо фото
        await callback.message.answer(
            f"<b>{stage['title']}</b>\n\n{stage['text']}",
            reply_markup=kb
        )
        await asyncio.sleep(2)
    
    await state.finish()
    await callback.answer()

async def tour_next(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

def register_tour_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_tour, lambda c: c.data == "tour")
    dp.register_callback_query_handler(begin_tour, lambda c: c.data == "tour_begin", state='*')
    dp.register_callback_query_handler(tour_next, lambda c: c.data == "tour_next", state=TourState.in_progress)