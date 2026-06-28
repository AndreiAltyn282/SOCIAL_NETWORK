from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Post
from comments.models import Comment
from .serializers import PostSerializer, PostCreateSerializer
from comments.serializers import CommentSerializer
from startup_packs.models import PackPost
from datetime import datetime

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'audience']
    search_fields = ['text']
    ordering_fields = ['created_at', 'likes_count']

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.all()
        if user.is_authenticated:
            return queryset.filter(
                models.Q(audience='public') |
                models.Q(author=user) |
                models.Q(audience='subscribers', author__in=user.following.all())
            ).distinct()
        return queryset.filter(audience='public')

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Лента с постами + постами из стартовых наборов"""
        user = request.user
        posts = []

        # 1. Обычные посты
        if user.is_authenticated:
            user_posts = Post.objects.filter(
                models.Q(audience='public') |
                models.Q(author=user) |
                models.Q(audience='subscribers', author__in=user.following.all())
            ).distinct()
        else:
            user_posts = Post.objects.filter(audience='public')

        for post in user_posts:
            posts.append({
                'id': f'post_{post.id}',
                'type': 'post',
                'created_at': post.created_at,
                'author': {
                    'id': post.author.id,
                    'username': post.author.username,
                    'avatar': post.author.avatar.url if post.author.avatar else None
                },
                'text': post.text,
                'image': post.image.url if post.image else None,
                'audience': post.audience,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'is_liked': post.likes.filter(id=user.id).exists() if user.is_authenticated else False,
                'is_author': post.author == user,
                'comments': [],
                'source_name': None,
                'is_ai_generated': False,
                'pack_name': None
            })

        # 2. Посты из стартовых наборов, на которые подписан пользователь
        if user.is_authenticated:
            user_packs = user.startup_packs.all().values_list('pack_id', flat=True)
            if user_packs:
                pack_posts = PackPost.objects.filter(pack_id__in=user_packs).order_by('-published_at')[:20]
                for pp in pack_posts:
                    posts.append({
                        'id': f'pack_{pp.id}',
                        'type': 'pack_post',
                        'created_at': pp.published_at,
                        'author': {
                            'id': user.id,
                            'username': user.username,
                            'avatar': user.avatar.url if user.avatar else None
                        },
                        'text': f'📦 {pp.title}\n\n{pp.content}\n\n🔗 Источник: {pp.source_name}',
                        'image': None,
                        'audience': 'public',
                        'likes_count': 0,
                        'comments_count': 0,
                        'is_liked': False,
                        'is_author': False,
                        'comments': [],
                        'source_name': pp.source_name,
                        'is_ai_generated': pp.is_ai_generated,
                        'pack_name': pp.pack.name
                    })

        # Сортируем по дате (новые сверху)
        posts = sorted(posts, key=lambda x: x['created_at'], reverse=True)

        return Response(posts)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            return Response({'status': 'unliked', 'likes_count': post.likes_count})
        post.likes.add(user)
        return Response({'status': 'liked', 'likes_count': post.likes_count})

    @action(detail=True, methods=['post'], parser_classes=[JSONParser])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(author=request.user, post=post)
            return Response(CommentSerializer(comment).data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all().order_by('-created_at')
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'author']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
