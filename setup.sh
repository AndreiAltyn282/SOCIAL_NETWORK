#!/bin/bash
# Универсальная установка проекта

echo "🔧 НАСТРОЙКА ПРОЕКТА"
echo "====================="

# 1. Создание виртуального окружения
echo "1️⃣ Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# 2. Обновление pip
echo "2️⃣ Обновление pip..."
pip install --upgrade pip

# 3. Установка зависимостей
echo "3️⃣ Установка зависимостей..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt не найден"
    # Устанавливаем базовые пакеты
    pip install django djangorestframework django-cors-headers
    pip install djangorestframework-simplejwt channels channels-redis
    pip install psycopg2-binary python-dotenv django-filter Pillow
    pip install requests
fi

# 4. Настройка .env
echo "4️⃣ Настройка .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "⚠️ .env.example не найден"
    echo "📝 Создан .env. Отредактируйте его!"
fi

# 5. Миграции
echo "5️⃣ Применение миграций..."
python manage.py makemigrations
python manage.py migrate

# 6. Создание суперпользователя
echo "6️⃣ Создание суперпользователя..."
python manage.py createsuperuser

# 7. Заполнение тестовыми данными
echo "7️⃣ Заполнение тестовыми данными..."
if [ -f "create_data.py" ]; then
    python manage.py shell < create_data.py
else
    echo "⚠️ create_data.py не найден"
fi

echo ""
echo "✅ НАСТРОЙКА ЗАВЕРШЕНА!"
echo "📌 Запуск проекта: source venv/bin/activate && python manage.py runserver"
