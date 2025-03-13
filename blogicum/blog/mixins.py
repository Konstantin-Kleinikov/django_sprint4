"""Миксины для приложения blog."""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Post


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        self.post_instance = self.get_object()
        if self.post_instance.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.post_instance.id
            )
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
