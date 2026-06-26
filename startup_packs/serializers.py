from rest_framework import serializers
from .models import StartupPack, UserStartupPack
from users.serializers import UserSerializer

class StartupPackSerializer(serializers.ModelSerializer):
    experts = UserSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    subscribers_count = serializers.IntegerField(source='user_startup_packs.count', read_only=True)
    
    class Meta:
        model = StartupPack
        fields = [
            'id', 'name', 'description', 'experts', 
            'subscribers_count', 'is_subscribed', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserStartupPack.objects.filter(
                user=request.user, 
                pack=obj
            ).exists()
        return False

class UserStartupPackSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки пользователя на стартовый набор"""
    user = UserSerializer(read_only=True)
    pack = StartupPackSerializer(read_only=True)
    
    class Meta:
        model = UserStartupPack
        fields = ['id', 'user', 'pack', 'subscribed_at']
        read_only_fields = ['subscribed_at']
