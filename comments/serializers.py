from rest_framework import serializers
from .models import Comment
from users.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'author', 'created_at', 'updated_at']

    def validate_text(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Комментарий не может быть пустым")
        return value.strip()
