# ChatProject/chat/views.py
from django.views.generic import TemplateView, CreateView, FormView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, ProfileForm
from .models import Message


# Home view: shows welcome message and recent chats if logged in.
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


# Login view using Django's built-in view.
class UserLoginView(LoginView):
    template_name = 'chat/login.html'


# Custom logout view to allow GET (if you prefer)
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('chat:home')


# Registration view.
class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('chat:profile_edit')


# Profile edit view.
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


# User search view.
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


# Chat conversation view.
class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/chat.html'
    login_url = reverse_lazy('chat:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        friend_individual_id = self.kwargs.get('friend_id')
        friend = get_object_or_404(User, profile__individual_id=friend_individual_id)
        context['friend'] = friend
        messages = Message.objects.filter(
            Q(sender=self.request.user, receiver=friend) | Q(sender=friend, receiver=self.request.user)
        ).order_by('timestamp')
        context['messages'] = messages
        return context
