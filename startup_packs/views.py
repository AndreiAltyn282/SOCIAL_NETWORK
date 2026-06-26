from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import StartupPack, UserStartupPack
from .serializers import StartupPackSerializer, UserStartupPackSerializer

class StartupPackViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления стартовыми наборами
    """
    queryset = StartupPack.objects.all().order_by('-created_at')
    serializer_class = StartupPackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Возвращает все стартовые наборы с подсчетом подписчиков"""
        return StartupPack.objects.all().prefetch_related('experts')

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Подписка на стартовый набор"""
        pack = self.get_object()
        user = request.user

        # Проверяем, есть ли уже подписка
        user_pack = UserStartupPack.objects.filter(user=user, pack=pack).first()
        
        if user_pack:
            # Если есть - отписываемся
            user_pack.delete()
            return Response({
                'status': 'unsubscribed',
                'message': f'Вы отписались от набора {pack.name}'
            })
        else:
            # Если нет - подписываемся
            UserStartupPack.objects.create(user=user, pack=pack)
            
            # Подписываем пользователя на всех экспертов в наборе
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
        """Возвращает список подписчиков набора"""
        pack = self.get_object()
        user_packs = UserStartupPack.objects.filter(pack=pack).select_related('user')
        serializer = UserStartupPackSerializer(user_packs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_packs(self, request):
        """Возвращает наборы, на которые подписан текущий пользователь"""
        user_packs = UserStartupPack.objects.filter(user=request.user).select_related('pack')
        packs = [up.pack for up in user_packs]
        serializer = self.get_serializer(packs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Рекомендует стартовые наборы для пользователя"""
        user = request.user
        # Получаем наборы, на которые пользователь еще не подписан
        subscribed_packs = UserStartupPack.objects.filter(user=user).values_list('pack_id', flat=True)
        recommended_packs = StartupPack.objects.exclude(id__in=subscribed_packs)[:5]
        serializer = self.get_serializer(recommended_packs, many=True)
        return Response(serializer.data)
