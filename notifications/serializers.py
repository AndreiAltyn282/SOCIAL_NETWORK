from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для уведомлений"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 
            'title', 'message', 'link', 
            'is_read', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        """Проверка данных перед созданием уведомления"""
        if not data.get('title'):
            raise serializers.ValidationError(
                "Заголовок уведомления обязателен"
            )
        if not data.get('message'):
            raise serializers.ValidationError(
                "Сообщение уведомления обязательно"
            )
        return data
