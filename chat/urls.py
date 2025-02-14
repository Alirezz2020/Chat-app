# ChatProject/chat/urls.py
from django.urls import path
from .views import (
    HomeView, UserLoginView, CustomLogoutView, RegisterView,
    ProfileEditView, SearchUserView, ChatView
)

app_name = 'chat'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('search/', SearchUserView.as_view(), name='search'),
    path('chat/<str:friend_id>/', ChatView.as_view(), name='chat'),
]
