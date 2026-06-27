import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from notifications.models import Notification

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        user = self.scope['user']

        message = await self.save_message(user, self.conversation_id, message_text)
        
        # СОЗДАЁМ УВЕДОМЛЕНИЯ ДЛЯ ВСЕХ УЧАСТНИКОВ ЧАТА
        await self.create_notifications(message, user)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': user.username,
                    'text': message.text,
                    'created_at': message.created_at.isoformat(),
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, user, conversation_id, text):
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=user,
            text=text
        )

    @database_sync_to_async
    def create_notifications(self, message, sender):
        conversation = message.conversation
        recipients = conversation.participants.exclude(id=sender.id)
        for recipient in recipients:
            Notification.objects.create(
                user=recipient,
                notification_type='message',
                title=f'Новое сообщение от {sender.username}',
                message=message.text[:100],
                link=f'/chat/{conversation.id}'
            )
