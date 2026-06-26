from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщений"""
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'text', 'is_read', 'created_at']
        read_only_fields = ['created_at']

    def validate_text(self, value):
        """Проверка, что текст не пустой"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value.strip()


class ConversationSerializer(serializers.ModelSerializer):
    """Сериализатор для чатов"""
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        """Возвращает последнее сообщение в чате"""
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        """Возвращает количество непрочитанных сообщений для текущего пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
