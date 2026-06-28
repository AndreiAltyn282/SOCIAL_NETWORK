from rest_framework import serializers
from .models import StartupPack, UserStartupPack, PackPost, PackPostLike, PackPostComment
from users.serializers import UserSerializer

class PackPostLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PackPostLike
        fields = ['id', 'user', 'created_at']


class PackPostCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PackPostComment
        fields = ['id', 'user', 'text', 'created_at']


class PackPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = PackPost
        fields = ['id', 'title', 'content', 'link', 'source_name', 'published_at', 
                  'is_ai_generated', 'likes_count', 'comments_count', 'is_liked']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class StartupPackSerializer(serializers.ModelSerializer):
    experts = UserSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    subscribers_count = serializers.IntegerField(source='user_startup_packs.count', read_only=True)
    posts = PackPostSerializer(many=True, read_only=True, source='rss_posts')

    class Meta:
        model = StartupPack
        fields = [
            'id', 'name', 'description', 'experts',
            'subscribers_count', 'is_subscribed',
            'created_at', 'updated_at', 'posts'
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
    user = UserSerializer(read_only=True)
    pack = StartupPackSerializer(read_only=True)

    class Meta:
        model = UserStartupPack
        fields = ['id', 'user', 'pack', 'subscribed_at']
        read_only_fields = ['subscribed_at']
