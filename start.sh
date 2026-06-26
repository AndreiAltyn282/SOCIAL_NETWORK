#!/bin/bash
# Универсальный скрипт запуска проекта

echo "🚀 ЗАПУСК ПРОЕКТА"
echo "=================="

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "⚠️ Виртуальное окружение не найдено. Создаём..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "📦 Активация виртуального окружения..."
source venv/bin/activate

# Проверяем установку зависимостей
if [ ! -f "requirements.txt" ]; then
    echo "⚠️ requirements.txt не найден"
else
    echo "📋 Установка зависимостей..."
    pip install -r requirements.txt
fi

# Проверяем миграции
echo "🔄 Проверка миграций..."
python manage.py makemigrations
python manage.py migrate

# Запускаем сервер
echo "🌐 Запуск Django сервера..."
python manage.py runserver