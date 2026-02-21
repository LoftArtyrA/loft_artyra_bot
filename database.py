import sqlite3
from datetime import datetime
from config import DATABASE_NAME, REFERRAL_BONUS_INVITER, REFERRAL_BONUS_INVITED

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        referral_code TEXT UNIQUE,
        referred_by INTEGER,
        bonus_balance INTEGER DEFAULT 0,
        quiz_completed BOOLEAN DEFAULT 0,
        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Таблица заказов
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        full_name TEXT,
        bed_size TEXT,
        construction TEXT,
        mattress TEXT,
        mattress_price INTEGER DEFAULT 0,
        fabric_shop TEXT,
        fabric_name TEXT,
        ral_color TEXT,
        pillows TEXT,
        comment TEXT,
        total INTEGER,
        discount INTEGER DEFAULT 0,
        prepayment INTEGER,
        status TEXT DEFAULT 'pending',
        paid BOOLEAN DEFAULT 0,
        receipt_file_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Таблица отзывов
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        rating INTEGER,
        text TEXT,
        photo_id TEXT,
        approved BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Таблица результатов квиза
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        q1 TEXT,
        q2 TEXT,
        q3 TEXT,
        q4 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

def save_user(user_id: int, username: str, full_name: str, referred_by: int = None):
    """Сохранение/обновление пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = c.fetchone()
    
    if exists:
        c.execute('''UPDATE users SET username = ?, full_name = ?, last_active = ?
                     WHERE user_id = ?''',
                  (username, full_name, datetime.now(), user_id))
    else:
        referral_code = f"LOFT{user_id}"
        c.execute('''INSERT INTO users (user_id, username, full_name, referral_code, referred_by)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, username, full_name, referral_code, referred_by))
        
        if referred_by:
            c.execute('''UPDATE users SET bonus_balance = bonus_balance + ?
                         WHERE user_id = ?''',
                      (REFERRAL_BONUS_INVITER, referred_by))
    
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Получить данные пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    
    conn.close()
    
    if user:
        return {
            'user_id': user[0],
            'username': user[1],
            'full_name': user[2],
            'referral_code': user[3],
            'referred_by': user[4],
            'bonus_balance': user[5],
            'quiz_completed': user[6],
            'first_seen': user[7],
            'last_active': user[8]
        }
    return None

def get_referrals_count(user_id: int):
    """Получить количество приглашенных"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM users WHERE referred_by = ?', (user_id,))
    count = c.fetchone()[0]
    
    conn.close()
    return count

def activate_referral_code(new_user_id: int, code: str):
    """Активация реферального кода"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users WHERE referral_code = ?', (code,))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False, "❌ Реферальный код не найден"
    
    inviter_id = result[0]
    
    if inviter_id == new_user_id:
        conn.close()
        return False, "❌ Нельзя использовать свой код"
    
    c.execute('SELECT referred_by FROM users WHERE user_id = ?', (new_user_id,))
    referred_by = c.fetchone()
    
    if referred_by and referred_by[0]:
        conn.close()
        return False, "❌ Вы уже использовали реферальный код"
    
    c.execute('UPDATE users SET referred_by = ? WHERE user_id = ?',
              (inviter_id, new_user_id))
    
    c.execute('UPDATE users SET bonus_balance = bonus_balance + ? WHERE user_id = ?',
              (REFERRAL_BONUS_INVITER, inviter_id))
    
    c.execute('UPDATE users SET bonus_balance = bonus_balance + ? WHERE user_id = ?',
              (REFERRAL_BONUS_INVITED, new_user_id))
    
    conn.commit()
    conn.close()
    
    return True, f"✅ Код активирован! Вы получили {REFERRAL_BONUS_INVITED}₽ бонуса"

def save_order(user_id: int, username: str, full_name: str, data: dict) -> int:
    """Сохранение заказа в БД"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO orders 
                 (user_id, username, full_name, bed_size, construction, mattress, 
                  mattress_price, fabric_shop, fabric_name, ral_color, pillows, 
                  comment, total, discount, prepayment, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, username, full_name, 
               data.get('bed_size'), data.get('construction'), data.get('mattress'),
               data.get('mattress_price', 0), data.get('fabric_shop', ''), 
               data.get('fabric_name', ''), data.get('ral_color', ''), data.get('pillows'),
               data.get('comment', ''), data.get('total'), data.get('discount', 0),
               data.get('prepayment'), 'pending'))
    
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return order_id

def get_user_orders(user_id: int):
    """Получить заказы пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''SELECT id, total, status, created_at FROM orders 
                 WHERE user_id = ? ORDER BY id DESC''', (user_id,))
    orders = c.fetchall()
    
    conn.close()
    return orders

def get_all_orders():
    """Получить все заказы"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''SELECT id, user_id, username, total, status, created_at 
                 FROM orders ORDER BY id DESC''')
    rows = c.fetchall()
    
    orders = []
    for row in rows:
        orders.append({
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'total': row[3],
            'status': row[4],
            'created_at': row[5]
        })
    
    conn.close()
    return orders

def get_order_by_id(order_id: int):
    """Получить заказ по ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    row = c.fetchone()
    
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'full_name': row[3],
            'bed_size': row[4],
            'construction': row[5],
            'mattress': row[6],
            'mattress_price': row[7],
            'fabric_shop': row[8],
            'fabric_name': row[9],
            'ral_color': row[10],
            'pillows': row[11],
            'comment': row[12],
            'total': row[13],
            'discount': row[14],
            'prepayment': row[15],
            'status': row[16],
            'paid': row[17],
            'receipt_file_id': row[18] if len(row) > 18 else None,
            'created_at': row[19] if len(row) > 19 else None,
            'updated_at': row[20] if len(row) > 20 else None
        }
    return None

def update_order_receipt(order_id: int, file_id: str):
    """Сохранить ID файла чека и обновить статус"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Проверяем, существует ли колонка receipt_file_id
    c.execute("PRAGMA table_info(orders)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'receipt_file_id' not in columns:
        # Добавляем колонку если её нет
        c.execute('ALTER TABLE orders ADD COLUMN receipt_file_id TEXT')
    
    c.execute('''UPDATE orders 
                 SET receipt_file_id = ?, status = 'receipt_uploaded', updated_at = ?
                 WHERE id = ?''',
              (file_id, datetime.now(), order_id))
    
    conn.commit()
    conn.close()

def update_order_status(order_id: int, status: str):
    """Обновить статус заказа"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''UPDATE orders 
                 SET status = ?, updated_at = ?
                 WHERE id = ?''',
              (status, datetime.now(), order_id))
    
    conn.commit()
    conn.close()

def get_stats():
    """Получить расширенную статистику"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM orders')
    total_orders = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM orders WHERE status = "completed"')
    completed_orders = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM orders WHERE status IN ("pending", "paid", "receipt_uploaded", "confirmed")')
    pending_orders = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM orders WHERE paid = 1 OR status IN ("confirmed", "completed")')
    paid_orders = c.fetchone()[0]
    
    c.execute('SELECT SUM(total) FROM orders')
    total_sum = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(total) FROM orders WHERE paid = 1 OR status IN ("confirmed", "completed")')
    paid_sum = c.fetchone()[0] or 0
    
    c.execute('SELECT AVG(rating) FROM reviews WHERE approved = 1')
    avg_rating = c.fetchone()[0] or 0
    
    c.execute('SELECT COUNT(*) FROM reviews')
    total_reviews = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'total_sum': total_sum,
        'paid_sum': paid_sum,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews
    }

def get_all_users_for_broadcast():
    """Получить всех пользователей для рассылки"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users')
    users = [row[0] for row in c.fetchall()]
    
    conn.close()
    return users

def save_quiz_result(user_id: int, q1, q2, q3, q4):
    """Сохранить результат квиза"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO quiz_results (user_id, q1, q2, q3, q4)
                 VALUES (?, ?, ?, ?, ?)''', (user_id, q1, q2, q3, q4))
    
    c.execute('UPDATE users SET quiz_completed = 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def save_review(user_id: int, username: str, rating: int, text: str, photo_id: str = None):
    """Сохранить отзыв"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''INSERT INTO reviews (user_id, username, rating, text, photo_id)
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, username, rating, text, photo_id))
    
    review_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return review_id

def get_approved_reviews(limit: int = 10):
    """Получить одобренные отзывы"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''SELECT username, rating, text, photo_id, created_at 
                 FROM reviews WHERE approved = 1 
                 ORDER BY created_at DESC LIMIT ?''', (limit,))
    reviews = c.fetchall()
    
    conn.close()
    return reviews