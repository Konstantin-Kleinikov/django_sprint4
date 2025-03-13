"""Модуль для представлений приложения blog."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CommentForm, EditProfileForm, PostForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Comment, Post
from .service import get_filtered_posts, get_paginated_posts

User = get_user_model()


def index(request):
    """Обрабатывает запрос к главной странице 'Лента записей'."""
    post_list = (get_filtered_posts(request, annotate=True)
                 )
    return render(
        request,
        'blog/index.html',
        {
            'page_obj': get_paginated_posts(request, post_list)
        }
    )


def post_detail(request, post_id: int):
    """Обрабатывает запрос к странице записи блога.

    Параметры:
            post_id (int): номер записи блога
    """
    post = get_object_or_404(
        get_filtered_posts(request, all_posts=True),
        pk=post_id
    )

    context = {
        'form': CommentForm(),
        'comments': Comment.objects.select_related('post').filter(post=post_id),
        'post': post
    }

    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Обрабатывает запрос к странице публикаций блогов по категории.

    Параметры:
             category_slug (slug): название категории записей блога
    """
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = (
        get_filtered_posts(request, annotate=True)
        .filter(category=category)
    )

    return render(request,
                  'blog/category.html',
                  {
                      'category': category,
                      'page_obj': get_paginated_posts(request, post_list),
                  }
                  )


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = (
        get_filtered_posts(request, all_posts=True, annotate=True)
        .filter(author=profile.pk)
    )
    context = {
        'profile': profile,
        'page_obj': get_paginated_posts(request, post_list)
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = EditProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


class PostCreateView(
    LoginRequiredMixin,
    PostMixin,
    CreateView
):

    def get_initial(self):
        initial = super().get_initial()
        initial['pub_date'] = timezone.now()
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class PostUpdateView(
    LoginRequiredMixin,
    PostMixin,
    UpdateView
):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = self.get_object()
        if self.post_instance.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.post_instance.id
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(
    LoginRequiredMixin,
    OnlyAuthorMixin,
    PostMixin,
    DeleteView
):
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_instance = self.get_object()
        context.update({
            'form': PostForm(instance=post_instance),
        })
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class CommentCreateView(
    LoginRequiredMixin,
    CommentMixin,
    CreateView
):
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
             Post,
             pk=self.kwargs['post_id']
         )
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin,
    OnlyAuthorMixin,
    CommentMixin,
    UpdateView
):

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def form_valid(self, form):
        #form.instance.id = self.comment.id
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(
    LoginRequiredMixin,
    OnlyAuthorMixin,
    CommentMixin,
    DeleteView
):
    pass
