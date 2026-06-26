from django.db import models
from django.conf import settings

class StartupPack(models.Model):
    """Модель стартового набора"""
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    experts = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='packs',
        limit_choices_to={'is_expert': True},
        verbose_name='Эксперты'
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
        """Количество подписчиков набора"""
        return self.user_startup_packs.count()


class UserStartupPack(models.Model):
    """Модель подписки пользователя на стартовый набор"""
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

    def save(self, *args, **kwargs):
        """При сохранении подписки автоматически подписываем на экспертов"""
        super().save(*args, **kwargs)
        # Подписываем пользователя на всех экспертов в наборе
        for expert in self.pack.experts.all():
            if expert != self.user:
                from subscriptions.models import Subscription
                Subscription.objects.get_or_create(
                    subscriber=self.user,
                    target=expert
                )
