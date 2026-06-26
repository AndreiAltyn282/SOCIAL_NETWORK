from django.db import models
from django.conf import settings

class Notification(models.Model):
    """
    Модель уведомления
    """
    NOTIFICATION_TYPES = [
        ('like', 'Лайк'),
        ('comment', 'Комментарий'),
        ('follow', 'Подписка'),
        ('message', 'Сообщение'),
        ('mention', 'Упоминание'),
        ('system', 'Системное'),
        ('pack', 'Стартовый набор'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES,
        verbose_name='Тип уведомления'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    link = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.title[:30]}...'

    @classmethod
    def create_notification(cls, user, notification_type, title, message, link=None):
        """
        Создает уведомление для пользователя
        """
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
