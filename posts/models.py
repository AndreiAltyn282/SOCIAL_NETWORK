from django.db import models
from django.conf import settings

class Post(models.Model):
    """
    Модель поста
    """
    AUDIENCE_CHOICES = [
        ('public', 'Публичный'),
        ('subscribers', 'Только подписчики'),
        ('private', 'Только я'),
    ]
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(
        upload_to='posts/', 
        null=True, 
        blank=True,
        verbose_name='Изображение'
    )
    audience = models.CharField(
        max_length=20, 
        choices=AUDIENCE_CHOICES, 
        default='public',
        verbose_name='Доступ'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='liked_posts', 
        blank=True,
        verbose_name='Лайки'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f'{self.author.username}: {self.text[:30]}...'

    @property
    def likes_count(self):
        """Количество лайков"""
        return self.likes.count()

    @property
    def comments_count(self):
        """Количество комментариев"""
        return self.comments.count()
