@echo off
echo ========================================
echo   УСТАНОВКА БОТА LOFT_ARTYRA
echo ========================================
echo.

echo [1/5] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [❌] Python не найден!
    echo Скачайте Python с python.org
    pause
    exit /b
)
echo [✅] Python найден

echo [2/5] Создание виртуального окружения...
python -m venv venv
echo [✅] Виртуальное окружение создано

echo [3/5] Активация виртуального окружения...
call venv\Scripts\activate.bat
echo [✅] Окружение активировано

echo [4/5] Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt
echo [✅] Зависимости установлены

echo.
echo ========================================
echo   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Отредактируйте файл config.py
echo 2. Запустите бота командой: python bot.py
echo.
pause