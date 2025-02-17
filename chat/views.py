
import json
from django.views.generic import TemplateView, CreateView, FormView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
class HomeView(TemplateView):
    template_name = 'chat/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Get conversation partner ids from sent and received messages.
            sent_ids = Message.objects.filter(sender=user).values_list('receiver', flat=True)
            received_ids = Message.objects.filter(receiver=user).values_list('sender', flat=True)
            conversation_ids = set(list(sent_ids) + list(received_ids))
            conversation_ids.discard(user.id)
            conversations = User.objects.filter(id__in=conversation_ids)
            conversation_data = []
            for friend in conversations:
                latest_message = Message.objects.filter(
                    Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
                ).order_by('-timestamp').first()
                unread_count = Message.objects.filter(sender=friend, receiver=user, status='sent').count()
                conversation_data.append({
                    'friend': friend,
                    'latest_message': latest_message,
                    'unread_count': unread_count,
                })
            conversation_data.sort(key=lambda c: c['latest_message'].timestamp if c['latest_message'] else 0,
                                   reverse=True)
            context['conversations'] = conversation_data
        return context
class UserLoginView(LoginView):
    template_name = 'chat/login.html'
class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('chat:dashboard')
class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('chat:profile_edit')
class ProfileEditView(LoginRequiredMixin, FormView):
    template_name = 'chat/profile_edit.html'
    form_class = ProfileForm
    success_url = reverse_lazy('chat:home')
    login_url = reverse_lazy('chat:login')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        profile = self.request.user.profile
        return form_class(instance=profile, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
class SearchUserView(LoginRequiredMixin, ListView):
    template_name = 'chat/search.html'
    context_object_name = 'users'
    model = User
    login_url = reverse_lazy('chat:login')

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return User.objects.filter(profile__individual_id__icontains=query)
        return User.objects.none()
@csrf_exempt
def edit_message(request, message_id):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        new_content = data.get('content')
        if new_content:
            message.edit_message(new_content)
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)
@csrf_exempt
def delete_message(request, message_id):
    if request.method == "POST" and request.user.is_authenticated:
        message = get_object_or_404(Message, id=message_id, sender=request.user)
        message.delete_message()
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)
class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/chat.html'
    login_url = 'chat:login'

    def dispatch(self, request, *args, **kwargs):
        friend_individual_id = self.kwargs.get('friend_id')
        friend = get_object_or_404(User, profile__individual_id=friend_individual_id)
        Message.objects.filter(sender=friend, receiver=request.user, status='sent').update(status='read')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        friend_individual_id = self.kwargs.get('friend_id')
        friend = get_object_or_404(User, profile__individual_id=friend_individual_id)
        context['friend'] = friend
        msgs = Message.objects.filter(
            Q(sender=self.request.user, receiver=friend) | Q(sender=friend, receiver=self.request.user)
        ).order_by('-timestamp')[:20]
        context['messages'] = list(reversed(msgs))
        return context
# Helper function to create system messages
def create_system_message(group, content):
    Message.objects.create(sender=None, group=group, content=content)
class CreateGroupView(LoginRequiredMixin, CreateView):
    model = GroupChat
    form_class = GroupChatForm
    template_name = 'chat/create_group.html'
    success_url = reverse_lazy('chat:dashboard')

    def form_valid(self, form):
        group = form.save(commit=False)
        group.owner = self.request.user
        group.save()
        GroupMembership.objects.create(user=self.request.user, group=group)
        create_system_message(group, f"{self.request.user.username} joined {group.group_name}")
        return super().form_valid(form)
@login_required
def group_search(request):
    query = request.GET.get('q', '')
    search_results = None
    if query:
        search_results = GroupChat.objects.filter(
            Q(group_id__icontains=query) | Q(group_name__icontains=query)
        )
    joined_groups = request.user.group_chats.all()  # groups user has joined
    return render(request, 'chat/group_search.html', {
        'search_results': search_results,
        'joined_groups': joined_groups,
        'query': query
    })
@login_required
def join_group(request, group_id):
    group = get_object_or_404(GroupChat, group_id=group_id)
    if request.user not in group.members.all():
        GroupMembership.objects.create(user=request.user, group=group)
        # Create a system message for join:
        Message.objects.create(sender=None, group=group, content=f"{request.user.username} joined {group.group_name}")
    return redirect('chat:group_chat', group_id=group.group_id)
@login_required
def leave_group(request, group_id):
    group = get_object_or_404(GroupChat, group_id=group_id)
    if request.user in group.members.all() and request.user != group.owner:
        membership = GroupMembership.objects.filter(user=request.user, group=group)
        if membership.exists():
            membership.delete()
            # Create a system message for leave:
            Message.objects.create(sender=None, group=group, content=f"{request.user.username} left {group.group_name}")
    return redirect('chat:dashboard')
class GroupEditView(LoginRequiredMixin, UpdateView):
    model = GroupChat
    form_class = GroupChatForm
    template_name = 'chat/edit_group.html'
    success_url = reverse_lazy('chat:dashboard')

    def get_object(self, queryset=None):
        group = get_object_or_404(GroupChat, group_id=self.kwargs.get('group_id'))
        if self.request.user != group.owner:
            raise PermissionError("Only the group owner can edit group info.")
        return group
@login_required
def delete_group(request, group_id):
    group = get_object_or_404(GroupChat, group_id=group_id)
    if request.user == group.owner:
        group.delete()
        return redirect('chat:dashboard')
    else:
        return JsonResponse({"error": "Only the group owner can delete this group."}, status=403)
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/dashboard.html'
    login_url = 'chat:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # One-to-one conversation list:
        sent_ids = Message.objects.filter(sender=user).values_list('receiver', flat=True)
        received_ids = Message.objects.filter(receiver=user).values_list('sender', flat=True)
        convo_ids = set(list(sent_ids) + list(received_ids))
        convo_ids.discard(user.id)
        conversations = User.objects.filter(id__in=convo_ids)
        convo_data = []
        for friend in conversations:
            latest = Message.objects.filter(
                Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
            ).order_by('-timestamp').first()
            unread = Message.objects.filter(sender=friend, receiver=user, status='sent').count()
            convo_data.append({
                'friend': friend,
                'latest_message': latest,
                'unread_count': unread,
            })
        convo_data.sort(key=lambda c: c['latest_message'].timestamp if c['latest_message'] else timezone.now(),
                        reverse=True)
        context['conversations'] = convo_data

        # Groups the user belongs to:
        context['groups'] = user.group_chats.all()
        return context
class ProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/profile.html'
    login_url = 'chat:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        profile_user = get_object_or_404(User, username=username)
        context['profile_user'] = profile_user
        return context
class GroupChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/group_chat.html'
    login_url = 'chat:login'

    def dispatch(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(GroupChat, group_id=group_id)
        # If the user is not a member, deny access or redirect to group search page.
        if request.user not in group.members.all():
            # Option 1: redirect to group search
            return redirect('chat:group_search')
            # Option 2: return an HTTP Forbidden response:
            # return HttpResponseForbidden("You are not a member of this group.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(GroupChat, group_id=group_id)
        context['group'] = group
        # Load group messages in chronological order
        context['messages'] = group.message_set.order_by('timestamp')
        # Create a mapping of member id to join date using the through model
        memberships = {gm.user.id: gm.joined_at for gm in group.groupmembership_set.all()}
        context['memberships'] = memberships
        return context
class GroupInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/group_info.html'
    login_url = 'chat:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(GroupChat, group_id=group_id)
        context['group'] = group
        context['members'] = group.members.all()
        # Create a dictionary: member.id -> joined_at
        memberships = {gm.user.id: gm.joined_at for gm in group.groupmembership_set.all()}
        context['memberships'] = memberships
        return context
