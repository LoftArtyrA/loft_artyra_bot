from config import PREPAYMENT_PERCENT

def calculate_total(data: dict) -> dict:
    """Расчет итоговой стоимости заказа"""
    base_prices = {
        "140x200": 41000,
        "160x200": 44000,
        "180x200": 48000,
        "200x200": 53000,
    }
    
    size = data.get('bed_size', '')
    base_price = base_prices.get(size, 0)
    mattress_price = data.get('mattress_price', 0)
    pillows_price = 3000 if data.get('pillows') == 'yes' else 0
    discount = data.get('discount', 0)
    
    total = base_price + mattress_price + pillows_price - discount
    if total < 0:
        total = 0
    
    prepayment = int(total * PREPAYMENT_PERCENT / 100)
    
    return {
        'base_price': base_price,
        'mattress_price': mattress_price,
        'pillows_price': pillows_price,
        'discount': discount,
        'total': total,
        'prepayment': prepayment
    }

def format_price(price: int) -> str:
    """Форматирование цены с пробелами"""
    return f"{price:,}".replace(',', ' ')

def format_order_summary(data: dict, prices: dict) -> str:
    """Форматирование сводки заказа"""
    
    mattress_display = data.get('mattress', 'Не выбран')
    if '|' in mattress_display:
        mattress_display = mattress_display.split('|')[-1].strip()
    
    summary = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃   🧾 ВАШ ЗАКАЗ          ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"🛏️ Размер: {data.get('bed_size')}\n"
        f"💰 Каркас: {format_price(prices['base_price'])} ₽\n\n"
        f"🔧 Конструкция:\n   {data.get('construction')}\n\n"
        f"💤 Матрас:\n   {mattress_display}\n"
    )
    
    if prices['mattress_price'] > 0:
        summary += f"   💰 {format_price(prices['mattress_price'])} ₽\n\n"
    else:
        summary += "\n"
    
    fabric_name = data.get('fabric_name', 'Не указана')
    fabric_shop = data.get('fabric_shop', 'Не указан')
    ral_color = data.get('ral_color', 'Не выбран')
    
    summary += (
        f"🎨 Обивка:\n"
        f"   Ткань: {fabric_name}\n"
        f"   Магазин: {fabric_shop}\n"
        f"   Цвет RAL: {ral_color}\n\n"
        f"🛏️ Подушки: {'Да (+3000₽)' if data.get('pillows') == 'yes' else 'Нет'}\n"
    )
    
    if data.get('comment'):
        summary += f"\n📝 Комментарий:\n   {data.get('comment')}\n"
    
    if prices['discount'] > 0:
        summary += f"\n🎁 Скидка: -{format_price(prices['discount'])} ₽\n"
    
    summary += (
        f"\n┏━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃ 💰 ИТОГО: {format_price(prices['total'])} ₽\n"
        f"┃ 💳 Предоплата: {format_price(prices['prepayment'])} ₽\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━┛"
    )
    
    return summary

def parse_referral_code(start_param: str) -> int:
    """Извлечение ID реферера из стартовой ссылки"""
    if start_param and start_param.startswith('ref'):
        try:
            return int(start_param[3:])
        except ValueError:
            pass
    return None