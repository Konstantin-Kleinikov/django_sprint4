"""Модуль с формами для приложения blog."""
from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={'cols': 22, 'rows': 5}),
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'is_published',
            'pub_date',
            'category',
            'location',
            'image'
        ]
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M:%S',
                attrs={'type': 'datetime-local'}
            )
        }
