#!/bin/bash

echo "========================================"
echo "  УСТАНОВКА БОТА LOFT_ARTYRA"
echo "========================================"
echo ""

echo "[1/5] Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "[❌] Python не найден!"
    echo "Установите Python: sudo apt install python3 python3-pip"
    exit 1
fi
echo "[✅] Python найден"

echo "[2/5] Создание виртуального окружения..."
python3 -m venv venv
echo "[✅] Виртуальное окружение создано"

echo "[3/5] Активация виртуального окружения..."
source venv/bin/activate
echo "[✅] Окружение активировано"

echo "[4/5] Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo "[✅] Зависимости установлены"

echo ""
echo "========================================"
echo "  УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!"
echo "========================================"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте файл config.py"
echo "2. Запустите бота командой: python3 bot.py"
echo ""