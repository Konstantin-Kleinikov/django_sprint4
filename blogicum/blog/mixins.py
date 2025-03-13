"""Миксины для приложения blog."""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Post, Comment


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


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
