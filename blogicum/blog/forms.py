"""Модуль с формами для приложения blog."""
from django.contrib.auth import get_user_model
from django import forms

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
        fields = ['title', 'text', 'pub_date', 'category', 'location', 'image']
        widgets = {'pub_date': forms.DateInput(attrs={'type': 'date'})}
