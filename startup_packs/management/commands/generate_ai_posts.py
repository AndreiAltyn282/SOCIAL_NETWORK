import requests
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from startup_packs.models import StartupPack, PackPost

User = get_user_model()

class Command(BaseCommand):
    help = 'Генерирует AI-посты для стартовых наборов'

    def handle(self, *args, **options):
        packs = StartupPack.objects.all()
        ai_user = User.objects.filter(is_superuser=True).first()

        if not ai_user:
            self.stdout.write(self.style.ERROR('❌ Нет суперпользователя для AI-постов'))
            return

        topics = [
            'тренды в IT',
            'новые технологии в маркетинге',
            'кейсы стартапов',
            'инструменты для дизайна',
            'аналитика данных 2026',
            'управление проектами',
            'бизнес-стратегии',
            'soft skills для лидеров'
        ]

        for pack in packs:
            try:
                topic = random.choice(topics)

                # Запрос к Ollama (если запущен локально)
                try:
                    response = requests.post(
                        'http://localhost:11434/api/generate',
                        json={
                            'model': 'llama3.2:3b',
                            'prompt': f'Напиши короткий, полезный пост для профессионального стартового набора "{pack.name}" на тему "{topic}". Пост должен быть информативным, экспертным, без рекламы. Объём: 100-200 слов.',
                            'stream': False,
                            'temperature': 0.7,
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        ai_text = response.json().get('response', '')
                    else:
                        ai_text = f'Полезный контент для стартового набора "{pack.name}" на тему "{topic}". Подписывайтесь, чтобы быть в курсе!'

                except:
                    ai_text = f'Свежий взгляд на тему "{topic}" для профессионалов. Присоединяйтесь к обсуждению в стартовом наборе "{pack.name}"!'

                # Создаём пост
                PackPost.objects.create(
                    pack=pack,
                    title=f'AI-дайджест: {topic}',
                    content=ai_text,
                    link='#',
                    source_name='AI-генератор',
                    published_at=timezone.now(),
                    is_ai_generated=True
                )

                self.stdout.write(self.style.SUCCESS(f'✅ AI-пост создан для "{pack.name}"'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка для {pack.name}: {e}'))
