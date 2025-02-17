# ChatProject/chat/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:friend_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/group/<str:group_id>/', consumers.GroupChatConsumer.as_asgi()),
]
