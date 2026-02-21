import sqlite3
import os
from config import DATABASE_NAME

def reset_orders():
    """Полное обнуление всех заказов"""
    print("=" * 50)
    print("🔄 ОБНУЛЕНИЕ СЧЕТЧИКА ЗАКАЗОВ")
    print("=" * 50)
    
    # Подключаемся к базе данных
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена по пути: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Получаем информацию о текущих заказах
    c.execute("SELECT COUNT(*) FROM orders")
    count_before = c.fetchone()[0]
    
    print(f"\n📊 Текущее количество заказов: {count_before}")
    
    if count_before == 0:
        print("✅ База данных уже пуста")
        conn.close()
        return
    
    # Показываем последние заказы перед удалением
    c.execute("SELECT id, user_id, total, status FROM orders ORDER BY id DESC LIMIT 5")
    last_orders = c.fetchall()
    
    if last_orders:
        print("\n📦 Последние заказы, которые будут удалены:")
        for order in last_orders:
            print(f"   #{order[0]} | Пользователь: {order[1]} | Сумма: {order[2]}₽ | Статус: {order[3]}")
    
    # Спрашиваем подтверждение
    print("\n⚠️  ВНИМАНИЕ! Это действие удалит ВСЕ заказы безвозвратно!")
    confirm = input("✅ Для подтверждения введите 'ДА': ")
    
    if confirm.upper() == "ДА":
        # Удаляем все заказы
        c.execute("DELETE FROM orders")
        conn.commit()
        
        # Сбрасываем автоинкремент (чтобы новые заказы начинались с 1)
        c.execute("DELETE FROM sqlite_sequence WHERE name='orders'")
        conn.commit()
        
        print(f"\n✅ Удалено заказов: {count_before}")
        print("✅ Счетчик сброшен! Новые заказы начнутся с №1")
    else:
        print("\n❌ Операция отменена")
    
    conn.close()
    
    # Проверяем результат
    c.execute("SELECT COUNT(*) FROM orders")
    count_after = c.fetchone()[0]
    print(f"\n📊 Текущее количество заказов после операции: {count_after}")

if __name__ == "__main__":
    reset_orders()