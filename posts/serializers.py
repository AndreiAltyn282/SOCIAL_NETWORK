from rest_framework import serializers
from .models import Post
from comments.models import Comment
from comments.serializers import CommentSerializer
from users.serializers import UserSerializer

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'text', 'image', 'audience', 
                 'created_at', 'updated_at', 'likes_count', 'comments_count',
                 'is_liked', 'is_author', 'comments']
        read_only_fields = ['created_at', 'updated_at']

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False

    def get_is_author(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.author == user
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['text', 'image', 'audience']
        extra_kwargs = {
            'text': {'required': False, 'allow_blank': True},
            'image': {'required': False},
            'audience': {'required': False},
        }

    def validate(self, data):
        text = data.get('text', '').strip()
        image = data.get('image')
        if not text and not image:
            raise serializers.ValidationError("Пост должен содержать текст или изображение")
        return data
