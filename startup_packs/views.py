from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import StartupPack, UserStartupPack, PackPost
from .serializers import StartupPackSerializer, PackPostSerializer

class PackPostViewSet(viewsets.ReadOnlyModelViewSet):
    """API для получения постов стартового набора"""
    queryset = PackPost.objects.all().order_by('-published_at')  # <-- ДОБАВЛЕНО!
    serializer_class = PackPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        pack_id = self.request.query_params.get('pack_id')
        if pack_id:
            return PackPost.objects.filter(pack_id=pack_id).order_by('-published_at')[:20]
        return PackPost.objects.all().order_by('-published_at')[:20]


class StartupPackViewSet(viewsets.ModelViewSet):
    queryset = StartupPack.objects.all().order_by('-created_at')
    serializer_class = StartupPackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'description']

    def get_queryset(self):
        return StartupPack.objects.all().prefetch_related('experts')

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        pack = self.get_object()
        user = request.user

        user_pack = UserStartupPack.objects.filter(user=user, pack=pack).first()

        if user_pack:
            user_pack.delete()
            return Response({
                'status': 'unsubscribed',
                'message': f'Вы отписались от набора {pack.name}'
            })
        else:
            UserStartupPack.objects.create(user=user, pack=pack)

            # Подписываем на всех экспертов в наборе
            for expert in pack.experts.all():
                if expert != user:
                    from subscriptions.models import Subscription
                    Subscription.objects.get_or_create(
                        subscriber=user,
                        target=expert
                    )

            return Response({
                'status': 'subscribed',
                'message': f'Вы подписались на набор {pack.name}'
            })

    @action(detail=True, methods=['get'])
    def subscribers(self, request, pk=None):
        pack = self.get_object()
        user_packs = UserStartupPack.objects.filter(pack=pack).select_related('user')
        return Response({
            'count': user_packs.count(),
            'users': [up.user.username for up in user_packs]
        })

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Возвращает посты для стартового набора"""
        pack = self.get_object()
        posts = pack.rss_posts.all().order_by('-published_at')[:20]
        serializer = PackPostSerializer(posts, many=True)
        return Response(serializer.data)
from .models import PackPost, PackPostLike, PackPostComment
from .serializers import PackPostSerializer, PackPostLikeSerializer, PackPostCommentSerializer

class PackPostViewSet(viewsets.ModelViewSet):
    queryset = PackPost.objects.all().order_by('-published_at')
    serializer_class = PackPostSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)

        like, created = PackPostLike.objects.get_or_create(post=post, user=user)
        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': post.likes.count()})
        return Response({'status': 'liked', 'likes_count': post.likes.count()})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)

        text = request.data.get('text')
        if not text or not text.strip():
            return Response({'error': 'Текст комментария обязателен'}, status=400)

        comment = PackPostComment.objects.create(post=post, user=user, text=text)
        serializer = PackPostCommentSerializer(comment)
        return Response(serializer.data, status=201)
