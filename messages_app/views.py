from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления чатами (Conversation)
    """
    queryset = Conversation.objects.all()  # <-- ДОБАВЛЯЕМ ЭТУ СТРОКУ
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает только чаты, в которых участвует текущий пользователь"""
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """Создает новый чат и добавляет текущего пользователя"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Добавляет участника в чат"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'Не указан user_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            conversation.participants.add(user)
            return Response({'status': 'Участник добавлен'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Удаляет участника из чата"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'Не указан user_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            conversation.participants.remove(user)
            return Response({'status': 'Участник удален'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления сообщениями
    """
    queryset = Message.objects.all()  # <-- ДОБАВЛЯЕМ ЭТУ СТРОКУ
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Возвращает только сообщения из чатов, где участвует текущий пользователь"""
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        """Создает новое сообщение от текущего пользователя"""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Отмечает сообщение как прочитанное"""
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'Сообщение отмечено как прочитанное'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Отмечает все сообщения пользователя как прочитанные"""
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'Не указан conversation_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = Message.objects.filter(
            conversation_id=conversation_id,
            is_read=False
        ).exclude(sender=request.user)
        
        count = messages.update(is_read=True)
        
        return Response({
            'status': f'Отмечено {count} сообщений как прочитанные'
        })
