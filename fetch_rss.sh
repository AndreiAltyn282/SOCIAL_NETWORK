#!/bin/bash
# ============================================
# Автоматический сбор RSS для стартовых наборов
# Запускается каждые 6 часов через cron
# ============================================

cd /home/andrey/social_network
source venv/bin/activate
python manage.py fetch_rss >> logs/rss.log 2>&1

# Добавляем дату в лог
echo "✅ RSS собран: $(date)" >> logs/rss.log
