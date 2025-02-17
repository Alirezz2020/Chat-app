# ChatProject/chat/urls.py
from django.urls import path
from .views import *
from . import views
app_name = 'chat'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('search/', SearchUserView.as_view(), name='search'),
    path('chat/<str:friend_id>/', ChatView.as_view(), name='chat'),
    path('group/<str:group_id>/', views.GroupChatView.as_view(), name='group_chat'),
    path('create_group/', views.CreateGroupView.as_view(), name='create_group'),
    path('group_search/', views.group_search, name='group_search'),
    path('join_group/<str:group_id>/', views.join_group, name='join_group'),
    path('leave_group/<str:group_id>/', views.leave_group, name='leave_group'),

    path('edit_group/<str:group_id>/', views.GroupEditView.as_view(), name='edit_group'),
    path('delete_group/<str:group_id>/', views.delete_group, name='delete_group'),
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('profile/<str:username>/', views.ProfilePageView.as_view(), name='profile_page'),

    path('group_info/<str:group_id>/', views.GroupInfoView.as_view(), name='group_info'),


]
