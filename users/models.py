from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    position = models.CharField(max_length=100, blank=True)
    skills = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_expert = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return self.username