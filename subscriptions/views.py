from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Subscription
from .serializers import SubscriptionSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subscriber', 'target']

    def get_queryset(self):
        """Возвращает только подписки текущего пользователя"""
        return Subscription.objects.filter(subscriber=self.request.user)

    def perform_create(self, serializer):
        """Создает подписку от текущего пользователя"""
        serializer.save(subscriber=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Переключает подписку на пользователя"""
        target_id = request.data.get('target_id')
        
        if not target_id:
            return Response(
                {'error': 'Не указан target_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            target = User.objects.get(id=target_id)
            
            if target == request.user:
                return Response(
                    {'error': 'Нельзя подписаться на себя'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверяем, есть ли уже подписка
            subscription = Subscription.objects.filter(
                subscriber=request.user,
                target=target
            ).first()
            
            if subscription:
                # Если есть - удаляем (отписываемся)
                subscription.delete()
                return Response({
                    'status': 'unsubscribed',
                    'message': f'Вы отписались от {target.username}'
                })
            else:
                # Если нет - создаем (подписываемся)
                Subscription.objects.create(
                    subscriber=request.user,
                    target=target
                )
                return Response({
                    'status': 'subscribed',
                    'message': f'Вы подписались на {target.username}'
                })
                
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def subscribers(self, request):
        """Возвращает список подписчиков текущего пользователя"""
        subscriptions = Subscription.objects.filter(target=request.user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def following(self, request):
        """Возвращает список пользователей, на которых подписан текущий пользователь"""
        subscriptions = Subscription.objects.filter(subscriber=request.user)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)
