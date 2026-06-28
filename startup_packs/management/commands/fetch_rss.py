import feedparser
import socket
import ssl
import urllib.request
from django.core.management.base import BaseCommand
from django.utils import timezone
from startup_packs.models import StartupPackSource, PackPost

class Command(BaseCommand):
    help = 'Собирает RSS-ленты для всех стартовых наборов'

    def handle(self, *args, **options):
        # Устанавливаем таймаут для всех сетевых операций
        socket.setdefaulttimeout(15)

        sources = StartupPackSource.objects.filter(is_active=True)
        total_posts = 0

        if not sources.exists():
            self.stdout.write(self.style.WARNING('❌ Нет активных RSS-источников. Добавьте их в админке.'))
            return

        for source in sources:
            self.stdout.write(f'📡 Обработка: {source.pack.name} - {source.name}')
            try:
                # Используем urllib для загрузки с таймаутом
                req = urllib.request.Request(
                    source.rss_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    content = response.read()

                # Парсим RSS без таймаута (он уже передан через socket)
                feed = feedparser.parse(content)

                if feed.bozo and feed.bozo_exception:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Ошибка RSS: {feed.bozo_exception}'))
                    continue

                count = 0
                for entry in feed.entries[:10]:
                    try:
                        post, created = PackPost.objects.get_or_create(
                            pack=source.pack,
                            link=entry.link,
                            defaults={
                                'title': entry.title,
                                'content': entry.summary or entry.description or 'Нет описания',
                                'source_name': source.name,
                                'published_at': timezone.now(),
                            }
                        )
                        if created:
                            count += 1
                            total_posts += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'    ⚠️ Ошибка сохранения: {e}'))
                        continue

                source.last_fetched = timezone.now()
                source.save()
                self.stdout.write(self.style.SUCCESS(f'  ✅ Добавлено {count} новых постов'))

            except socket.timeout:
                self.stdout.write(self.style.ERROR(f'  ❌ Таймаут (пропускаем): {source.rss_url}'))
            except ssl.SSLError:
                self.stdout.write(self.style.ERROR(f'  ❌ SSL ошибка (пропускаем): {source.rss_url}'))
            except urllib.error.HTTPError as e:
                self.stdout.write(self.style.ERROR(f'  ❌ HTTP ошибка {e.code}: {source.rss_url}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Всего добавлено {total_posts} постов'))
