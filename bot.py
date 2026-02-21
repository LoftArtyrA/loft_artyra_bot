from flask import Flask
import threading
import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from database import init_db
from handlers import register_all_handlers

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.API_TOKEN, parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    
    init_db()
    register_all_handlers(dp)
    
    print("🚀 Бот запущен!")
    await dp.start_polling()
# --- Эмуляция веб-сервера для Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/healthcheck')
def healthcheck():
    return "OK", 200

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# Запускаем веб-сервер в отдельном потоке
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------
if __name__ == '__main__':
    asyncio.run(main())
