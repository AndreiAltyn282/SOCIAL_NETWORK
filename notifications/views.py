from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления уведомлениями
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'is_read', 'notification_type']

    def get_queryset(self):
        """Возвращает только уведомления текущего пользователя"""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """Создает уведомление для пользователя"""
        serializer.save()

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Отмечает все уведомления пользователя как прочитанные"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'status': 'success',
            'message': f'Отмечено {count} уведомлений как прочитанные'
        })

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Отмечает конкретное уведомление как прочитанное"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({
            'status': 'success',
            'message': 'Уведомление отмечено как прочитанное'
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Возвращает количество непрочитанных уведомлений"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Возвращает все непрочитанные уведомления"""
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
