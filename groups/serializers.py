from rest_framework import serializers
from .models import Group, GroupPost
from users.serializers import UserSerializer

class GroupPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = GroupPost
        fields = ['id', 'author', 'text', 'image', 'created_at']

class GroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    members_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'avatar', 'creator', 'members_count', 'is_member', 'is_private', 'created_at']

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.members.all()
        return False
