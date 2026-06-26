from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'text_preview', 'audience', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['audience', 'created_at']
    search_fields = ['author__username', 'text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('author', 'text', 'image')
        }),
        ('Настройки доступа', {
            'fields': ('audience',)
        }),
        ('Статистика', {
            'fields': ('likes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст поста'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Лайков'

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Комментариев'
