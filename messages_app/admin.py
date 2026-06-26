from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participants_list', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at']

    def participants_list(self, obj):
        return ', '.join([user.username for user in obj.participants.all()])
    participants_list.short_description = 'Участники'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'text_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'text']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст сообщения'
