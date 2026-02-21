from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import save_quiz_result

class QuizState(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    result = State()

QUESTIONS = {
    1: {
        "text": "❓ Вопрос 1/4: Какой размер спальни?",
        "options": [
            ("📏 Маленькая (до 12м²)", "small"),
            ("📐 Средняя (12-18м²)", "medium"),
            ("📏 Большая (более 18м²)", "large")
        ]
    },
    2: {
        "text": "❓ Вопрос 2/4: Сколько человек будет спать?",
        "options": [
            ("👤 Один", "1"),
            ("👥 Двое", "2")
        ]
    },
    3: {
        "text": "❓ Вопрос 3/4: Какой стиль интерьера?",
        "options": [
            ("🏭 Лофт", "loft"),
            ("⬜ Минимализм", "minimal"),
            ("✨ Современный", "modern"),
            ("🏛️ Классика", "classic")
        ]
    },
    4: {
        "text": "❓ Вопрос 4/4: Какой бюджет?",
        "options": [
            ("💰 До 50 000₽", "low"),
            ("💎 50-70 000₽", "mid"),
            ("👑 Более 70 000₽", "high")
        ]
    }
}

RECOMMENDATIONS = {
    ("small", "1", "loft", "low"): {
        "size": "140x200",
        "construction": "На 5 ножках",
        "mattress": "Стандарт 2",
        "text": "Компактная кровать для небольшой спальни в стиле лофт. Идеально впишется!"
    },
    ("small", "1", "minimal", "low"): {
        "size": "140x200",
        "construction": "Крепление к стене",
        "mattress": "Стандарт 1",
        "text": "Минималистичная кровать, визуально расширяющая пространство."
    },
    ("medium", "2", "loft", "mid"): {
        "size": "160x200",
        "construction": "Крепление к стене",
        "mattress": "Sonis Soft",
        "text": "Оптимальный выбор для спальни среднего размера. Комфорт и стиль."
    },
    ("medium", "2", "modern", "mid"): {
        "size": "160x200",
        "construction": "На 5 ножках",
        "mattress": "Flex 4",
        "text": "Современная кровать с эффектом парения. Отличный вариант!"
    },
    ("large", "2", "loft", "high"): {
        "size": "200x200",
        "construction": "Крепление к стене",
        "mattress": "Lovely Люкс",
        "text": "Премиальная кровать для просторной спальни. Максимальный комфорт!"
    }
}

async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await QuizState.question1.set()
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    for text, value in QUESTIONS[1]["options"]:
        kb.add(types.InlineKeyboardButton(text, callback_data=f"quiz1_{value}"))
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"))
    
    await callback.message.edit_text(
        "🎯 <b>ПОДБОР ИДЕАЛЬНОЙ КРОВАТИ (в доработке)</b>\n\n"
        "Ответьте на 4 вопроса, и я подберу оптимальный вариант!\n\n"
        f"{QUESTIONS[1]['text']}",
        reply_markup=kb
    )
    await callback.answer()

async def process_quiz1(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data.replace('quiz1_', '')
    await state.update_data(q1=answer)
    await QuizState.question2.set()
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    for text, value in QUESTIONS[2]["options"]:
        kb.add(types.InlineKeyboardButton(text, callback_data=f"quiz2_{value}"))
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"))
    
    await callback.message.edit_text(
        QUESTIONS[2]['text'],
        reply_markup=kb
    )
    await callback.answer()

async def process_quiz2(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data.replace('quiz2_', '')
    await state.update_data(q2=answer)
    await QuizState.question3.set()
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    for text, value in QUESTIONS[3]["options"]:
        kb.add(types.InlineKeyboardButton(text, callback_data=f"quiz3_{value}"))
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"))
    
    await callback.message.edit_text(
        QUESTIONS[3]['text'],
        reply_markup=kb
    )
    await callback.answer()

async def process_quiz3(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data.replace('quiz3_', '')
    await state.update_data(q3=answer)
    await QuizState.question4.set()
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    for text, value in QUESTIONS[4]["options"]:
        kb.add(types.InlineKeyboardButton(text, callback_data=f"quiz4_{value}"))
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over"))
    
    await callback.message.edit_text(
        QUESTIONS[4]['text'],
        reply_markup=kb
    )
    await callback.answer()

async def process_quiz4(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data.replace('quiz4_', '')
    data = await state.get_data()
    
    key = (data['q1'], data['q2'], data['q3'], answer)
    rec = RECOMMENDATIONS.get(key, RECOMMENDATIONS.get(("medium", "2", "loft", "mid")))
    
    save_quiz_result(callback.from_user.id, data['q1'], data['q2'], data['q3'], answer)
    
    text = (
        f"🎯 <b>ВАШ ИДЕАЛЬНЫЙ ВАРИАНТ! (в доработке)</b>\n\n"
        f"🛏️ <b>Размер:</b> {rec['size']}\n"
        f"🔧 <b>Конструкция:</b> {rec['construction']}\n"
        f"💤 <b>Матрас:</b> {rec['mattress']}\n\n"
        f"📝 <b>Рекомендация:</b>\n{rec['text']}\n\n"
        f"🎁 <b>Скидка за прохождение квиза: 500₽</b>\n\n"
        f"<i>⚙️ Функция находится в доработке</i>"
    )
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🛏️ Заказать эту кровать", callback_data="order_from_quiz"),
        types.InlineKeyboardButton("🔄 Пройти заново", callback_data="start_quiz"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="start_over")
    )
    
    await state.update_data(quiz_result=rec, discount=500)
    await callback.message.edit_text(text, reply_markup=kb)
    await state.finish()
    await callback.answer()

async def order_from_quiz(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rec = data.get('quiz_result', {})
    
    if rec:
        await state.update_data(
            bed_size=rec['size'],
            construction=rec['construction'],
            mattress=rec['mattress'],
            discount=500
        )
    
    from handlers.order import OrderState
    await OrderState.partner.set()
    
    from keyboards import partner_choice_keyboard
    await callback.message.edit_text(
        "✅ Данные из квиза загружены!\n\n"
        "🏬 Выберите магазин ткани:",
        reply_markup=partner_choice_keyboard()
    )
    await callback.answer()

def register_quiz_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_quiz, lambda c: c.data == "start_quiz", state='*')
    dp.register_callback_query_handler(process_quiz1, lambda c: c.data.startswith('quiz1_'), state=QuizState.question1)
    dp.register_callback_query_handler(process_quiz2, lambda c: c.data.startswith('quiz2_'), state=QuizState.question2)
    dp.register_callback_query_handler(process_quiz3, lambda c: c.data.startswith('quiz3_'), state=QuizState.question3)
    dp.register_callback_query_handler(process_quiz4, lambda c: c.data.startswith('quiz4_'), state=QuizState.question4)
    dp.register_callback_query_handler(order_from_quiz, lambda c: c.data == "order_from_quiz", state='*')