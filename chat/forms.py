# ChatProject/chat/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text="Minimum 6 characters."
    )
    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'image', 'individual_id']
        # Optionally, make individual_id read-only:
        # widgets = {'individual_id': forms.TextInput(attrs={'readonly': 'readonly'})}

    def clean_individual_id(self):
        individual_id = self.cleaned_data.get('individual_id')
        if not individual_id:
            raise ValidationError("Individual ID is required.")
        qs = Profile.objects.filter(individual_id=individual_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("This Individual ID is already taken.")
        return individual_id
class GroupChatForm(forms.ModelForm):
    class Meta:
        model = GroupChat
        fields = ['group_id', 'group_name', 'bio', 'image']
        widgets = {
            'group_id': forms.TextInput(attrs={'placeholder': 'Unique Group ID (no spaces)'}),
            'group_name': forms.TextInput(attrs={'placeholder': 'Group Name'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Group bio (optional)', 'rows': 3}),
        }

    def clean_group_id(self):
        group_id = self.cleaned_data.get('group_id')
        if " " in group_id:
            raise forms.ValidationError("Group ID cannot contain spaces.")
        return group_id