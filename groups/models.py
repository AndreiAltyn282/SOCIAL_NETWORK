from django.db import models
from django.conf import settings

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    avatar = models.ImageField(upload_to='groups/', null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='user_groups',  # <-- ИЗМЕНЕНО С 'groups' НА 'user_groups'
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def members_count(self):
        return self.members.count()

class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='groups_posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.text[:30]}...'
