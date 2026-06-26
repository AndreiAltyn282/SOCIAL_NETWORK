import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Получаем токен из query параметров
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        user = None
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await self.get_user(user_id)
                print(f"✅ User authenticated: {user.username}")
            except Exception as e:
                print(f"❌ Ошибка аутентификации: {e}")
                user = AnonymousUser()
        else:
            print("❌ Токен не передан")
            user = AnonymousUser()

        if user.is_anonymous:
            await self.close()
            return

        self.scope['user'] = user

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ WebSocket CONNECTED for user: {user.username}")

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

    async def disconnect(self, close_code):
        print(f"❌ WebSocket DISCONNECTED")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        user = self.scope.get('user')

        if user.is_anonymous:
            return

        message = await self.save_message(user, self.conversation_id, message_text)

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
