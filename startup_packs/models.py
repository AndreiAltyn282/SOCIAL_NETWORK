from django.db import models
from django.conf import settings

class StartupPack(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    experts = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='packs',
        limit_choices_to={'is_expert': True},
        verbose_name='Эксперты',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Стартовый набор'
        verbose_name_plural = 'Стартовые наборы'

    def __str__(self):
        return self.name

    @property
    def subscribers_count(self):
        return self.user_startup_packs.count()


class UserStartupPack(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='startup_packs'
    )
    pack = models.ForeignKey(
        StartupPack,
        on_delete=models.CASCADE,
        related_name='user_startup_packs'
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'pack']
        ordering = ['-subscribed_at']
        verbose_name = 'Подписка на стартовый набор'
        verbose_name_plural = 'Подписки на стартовые наборы'

    def __str__(self):
        return f'{self.user.username} -> {self.pack.name}'


# ========== НОВЫЕ МОДЕЛИ ДЛЯ RSS ==========

class StartupPackSource(models.Model):
    """Источник RSS для стартового набора"""
    pack = models.ForeignKey(
        StartupPack,
        on_delete=models.CASCADE,
        related_name='sources'
    )
    name = models.CharField(max_length=100, verbose_name='Название источника')
    rss_url = models.URLField(verbose_name='RSS-лента')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    last_fetched = models.DateTimeField(null=True, blank=True, verbose_name='Последний сбор')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Источник RSS'
        verbose_name_plural = 'Источники RSS'

    def __str__(self):
        return f'{self.pack.name} - {self.name}'


class PackPost(models.Model):
    """Пост из RSS для стартового набора"""
    pack = models.ForeignKey(
        StartupPack,
        on_delete=models.CASCADE,
        related_name='rss_posts'
    )
    title = models.CharField(max_length=500, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    link = models.URLField(verbose_name='Ссылка')
    source_name = models.CharField(max_length=100, verbose_name='Источник')
    published_at = models.DateTimeField(verbose_name='Дата публикации')
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_generated = models.BooleanField(default=False, verbose_name='Создано AI')

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Пост из RSS'
        verbose_name_plural = 'Посты из RSS'

    def __str__(self):
        return self.title[:50]

class PackPostLike(models.Model):
    """Лайк для поста из стартового набора"""
    post = models.ForeignKey(PackPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']


class PackPostComment(models.Model):
    """Комментарий к посту из стартового набора"""
    post = models.ForeignKey(PackPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
