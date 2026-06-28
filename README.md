# 🚀 ProSocial — Профессиональная социальная сеть

**ProSocial** — это гибридная платформа, объединяющая лучшие черты **Telegram** (мессенджер), **ВКонтакте** (сообщество) и **LinkedIn** (профессиональные связи).

Проект создавался как MVP для быстрого нетворкинга с уникальной фишкой — **«Стартовые наборы»** (подписка на экспертов одним кликом).

---

## ✨ Возможности

- ✅ Регистрация и вход (JWT)
- ✅ Лента постов (текст + изображения)
- ✅ Лайки и комментарии
- ✅ Профиль пользователя (аватар, должность, навыки)
- ✅ Редактирование профиля
- ✅ WebSocket-чат в реальном времени
- ✅ Уведомления
- ✅ Стартовые наборы (подписка на экспертов)
- ✅ RSS-сборщик контента
- ✅ AI-генерация постов (Ollama)
- ✅ Поиск по постам
- ✅ Тёмная тема
- ✅ Адаптивная вёрстка

---

## 🛠️ Стек технологий

| Компонент | Технология |
|-----------|------------|
| **Бэкенд** | Django 5.0 + Django REST Framework |
| **База данных** | PostgreSQL |
| **WebSocket** | Django Channels + Redis (InMemory для разработки) |
| **Фронтенд** | React + TypeScript + Material-UI |
| **AI-генерация** | Ollama (локально) или OpenAI API |
| **Деплой** | GitHub + Back4app / VPS (Yandex Cloud / VK Cloud) |

---

## 🚀 Быстрый старт

### Клонирование проекта

```bash
git clone https://github.com/AndreiAltyn282/SOCIAL_NETWORK.git
cd SOCIAL_NETWORK
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 AndreiAltyn282

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
