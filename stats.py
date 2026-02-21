import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_NAME
import os

def get_stats():
    """Получить статистику по боту"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Общая статистика
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'confirmed'")
    paid_orders = c.fetchone()[0]
    
    # Активность за последние 24 часа
    yesterday = datetime.now() - timedelta(days=1)
    c.execute("SELECT COUNT(*) FROM users WHERE last_active > ?", (yesterday,))
    active_24h = c.fetchone()[0]
    
    # Активность за последние 7 дней
    week_ago = datetime.now() - timedelta(days=7)
    c.execute("SELECT COUNT(*) FROM users WHERE last_active > ?", (week_ago,))
    active_7d = c.fetchone()[0]
    
    # Новые пользователи по дням
    c.execute("""
        SELECT date(first_seen), COUNT(*) 
        FROM users 
        GROUP BY date(first_seen) 
        ORDER BY date(first_seen) DESC 
        LIMIT 7
    """)
    new_users_daily = c.fetchall()
    
    # Заказы по дням
    c.execute("""
        SELECT date(created_at), COUNT(*) 
        FROM orders 
        GROUP BY date(created_at) 
        ORDER BY date(created_at) DESC 
        LIMIT 7
    """)
    orders_daily = c.fetchall()
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'active_24h': active_24h,
        'active_7d': active_7d,
        'new_users_daily': new_users_daily,
        'orders_daily': orders_daily
    }

def show_stats():
    """Показать статистику в консоли"""
    stats = get_stats()
    
    print("\n" + "="*50)
    print("📊 СТАТИСТИКА БОТА")
    print("="*50)
    print(f"👥 Всего пользователей: {stats['total_users']}")
    print(f"📦 Всего заказов: {stats['total_orders']}")
    print(f"💰 Оплаченных заказов: {stats['paid_orders']}")
    print(f"🟢 Активных за 24ч: {stats['active_24h']}")
    print(f"📈 Активных за 7 дней: {stats['active_7d']}")
    print("-"*50)
    
    print("\n📅 Новые пользователи по дням:")
    for date, count in stats['new_users_daily']:
        print(f"   {date}: +{count}")
    
    print("\n📦 Заказы по дням:")
    for date, count in stats['orders_daily']:
        print(f"   {date}: {count}")
    
    print("="*50)

def export_stats_to_file():
    """Экспорт статистики в файл"""
    stats = get_stats()
    
    filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("📊 СТАТИСТИКА БОТА Loft_ArtyrA\n")
        f.write("="*50 + "\n")
        f.write(f"Дата отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        f.write(f"👥 Всего пользователей: {stats['total_users']}\n")
        f.write(f"📦 Всего заказов: {stats['total_orders']}\n")
        f.write(f"💰 Оплаченных заказов: {stats['paid_orders']}\n")
        f.write(f"🟢 Активных за 24ч: {stats['active_24h']}\n")
        f.write(f"📈 Активных за 7 дней: {stats['active_7d']}\n\n")
        
        f.write("📅 Новые пользователи по дням:\n")
        for date, count in stats['new_users_daily']:
            f.write(f"   {date}: +{count}\n")
        
        f.write("\n📦 Заказы по дням:\n")
        for date, count in stats['orders_daily']:
            f.write(f"   {date}: {count}\n")
    
    print(f"✅ Статистика сохранена в файл: {filename}")
    return filename

if __name__ == "__main__":
    show_stats()
