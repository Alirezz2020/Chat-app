
from django.contrib.auth.models import User
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import GroupChat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.friend_id = self.scope['url_route']['kwargs']['friend_id']
        print("Attempting WebSocket connection with friend_id:", self.friend_id)
        self.room_name = await self.get_room_name(self.scope['user'], self.friend_id)
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print("WebSocket connection accepted for room:", self.room_group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        attachment = data.get('attachment')
        sender_username = self.scope['user'].username
        # Save message to DB
        message_obj = await self.create_message(self.scope['user'], self.friend_id, message_text)
        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': sender_username,
                'message_id': message_obj.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event.get('message_id'),
        }))

    @sync_to_async
    def get_room_name(self, user, friend_id):
        try:
            friend = User.objects.get(profile__individual_id=friend_id)
            friend_username = friend.username
        except User.DoesNotExist:
            friend_username = 'unknown'
        # Sort usernames to create a unique room name.
        users = sorted([user.username, friend_username])
        return '_'.join(users)

    @sync_to_async
    def create_message(self, sender, friend_id, message):
        friend = User.objects.get(profile__individual_id=friend_id)
        return Message.objects.create(sender=sender, receiver=friend, content=message)
class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'group_{self.group_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print("Group chat connected:", self.room_group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        sender_username = self.scope['user'].username
        message_obj = await self.create_group_message(self.scope['user'], self.group_id, message_text)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'group_message',
                'message': message_text,
                'sender': sender_username,
                'message_id': message_obj.id,
                'status': message_obj.status,
            }
        )

    async def group_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def create_group_message(self, sender, group_id, message):
        group = GroupChat.objects.get(group_id=group_id)
        return Message.objects.create(sender=sender, group=group, content=message)