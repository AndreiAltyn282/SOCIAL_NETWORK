from rest_framework import serializers
from .models import Subscription
from users.serializers import UserSerializer

class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    subscriber = UserSerializer(read_only=True)
    target = UserSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'subscriber', 'target', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        """Проверка, что пользователь не подписывается на себя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            target = data.get('target')
            if target == request.user:
                raise serializers.ValidationError(
                    "Нельзя подписаться на себя"
                )
        return data
