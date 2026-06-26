from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from posts.models import Post
from comments.models import Comment
from messages_app.models import Conversation, Message
from subscriptions.models import Subscription
from startup_packs.models import StartupPack, UserStartupPack
from notifications.models import Notification
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('🗑️ Очищаем существующие данные...')
        
        # Проверяем существование таблиц перед очисткой
        tables = connection.introspection.table_names()
        
        if 'subscriptions_subscription' in tables:
            Subscription.objects.all().delete()
        
        if 'startup_packs_userstartuppack' in tables:
            UserStartupPack.objects.all().delete()
            
        if 'startup_packs_startuppack' in tables:
            StartupPack.objects.all().delete()
            
        if 'notifications_notification' in tables:
            Notification.objects.all().delete()
            
        if 'messages_app_message' in tables:
            Message.objects.all().delete()
            
        if 'messages_app_conversation' in tables:
            Conversation.objects.all().delete()
            
        if 'comments_comment' in tables:
            Comment.objects.all().delete()
            
        if 'posts_post' in tables:
            Post.objects.all().delete()

        # Удаляем старых пользователей (кроме суперпользователей)
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write('👥 Создание пользователей...')
        
        # Создаём экспертов
        experts = []
        for i in range(10):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                is_expert=True,
                position=fake.job(),
                bio=fake.paragraph(nb_sentences=3)
            )
            experts.append(user)
            self.stdout.write(f'  ✅ Эксперт {i+1}: {user.username}')

        # Создаём обычных пользователей
        users = []
        for i in range(30):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                position=fake.job() if random.random() > 0.3 else '',
                bio=fake.paragraph(nb_sentences=2) if random.random() > 0.5 else ''
            )
            users.append(user)
            if i % 10 == 0:
                self.stdout.write(f'  ✅ Пользователи: {i+1}/30')

        all_users = users + experts

        self.stdout.write('📝 Создание постов...')
        post_count = 0
        for user in all_users:
            for _ in range(random.randint(2, 5)):
                audience = random.choice(['public', 'public', 'public', 'subscribers'])
                post = Post.objects.create(
                    author=user,
                    text=fake.paragraph(nb_sentences=random.randint(3, 8)),
                    audience=audience
                )
                post_count += 1
                # Добавляем лайки
                for _ in range(random.randint(0, min(10, len(all_users)))):
                    if random.random() > 0.5:
                        liker = random.choice(all_users)
                        if liker != user:
                            post.likes.add(liker)
        self.stdout.write(f'  ✅ Создано {post_count} постов')

        self.stdout.write('💬 Создание комментариев...')
        comment_count = 0
        for post in Post.objects.all():
            for _ in range(random.randint(0, 5)):
                if random.random() > 0.3:
                    author = random.choice(all_users)
                    Comment.objects.create(
                        post=post,
                        author=author,
                        text=fake.paragraph(nb_sentences=random.randint(1, 3))
                    )
                    comment_count += 1
        self.stdout.write(f'  ✅ Создано {comment_count} комментариев')

        self.stdout.write('📦 Создание стартовых наборов...')
        for i in range(3):
            pack = StartupPack.objects.create(
                name=f'Pack {i+1}: {fake.word().capitalize()}',
                description=fake.paragraph(nb_sentences=2)
            )
            start_idx = i * 3
            end_idx = min(start_idx + 3, len(experts))
            pack.experts.set(experts[start_idx:end_idx])
            self.stdout.write(f'  ✅ {pack.name} создан')

        self.stdout.write('📨 Создание чатов и сообщений...')
        for user in users[:10]:
            for _ in range(random.randint(1, 3)):
                other_user = random.choice(all_users)
                if other_user != user:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(user, other_user)
                    for _ in range(random.randint(3, 10)):
                        sender = random.choice([user, other_user])
                        Message.objects.create(
                            conversation=conversation,
                            sender=sender,
                            text=fake.sentence()
                        )
        self.stdout.write('  ✅ Чаты и сообщения созданы')

        self.stdout.write('🔄 Создание подписок...')
        for user in users:
            for _ in range(random.randint(0, 10)):
                if random.random() > 0.5:
                    target = random.choice(all_users)
                    if target != user:
                        Subscription.objects.get_or_create(
                            subscriber=user,
                            target=target
                        )

        self.stdout.write('🔔 Создание уведомлений...')
        for user in users[:10]:
            for _ in range(random.randint(1, 3)):
                Notification.objects.create(
                    user=user,
                    notification_type=random.choice(['like', 'comment', 'follow', 'message']),
                    title=fake.sentence(nb_words=4),
                    message=fake.paragraph(nb_sentences=1),
                    is_read=random.choice([True, False])
                )

        self.stdout.write(self.style.SUCCESS('\n✅ Заполнение БД завершено!'))
        self.stdout.write(f'📊 Статистика:')
        self.stdout.write(f'  👥 Пользователей: {User.objects.count()}')
        self.stdout.write(f'  📝 Постов: {Post.objects.count()}')
        self.stdout.write(f'  💬 Комментариев: {Comment.objects.count()}')
        self.stdout.write(f'  📦 Стартовых наборов: {StartupPack.objects.count()}')
        self.stdout.write(f'  📨 Сообщений: {Message.objects.count()}')
        self.stdout.write(f'  🔔 Уведомлений: {Notification.objects.count()}')
