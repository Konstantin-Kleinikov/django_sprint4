"""Модуль для представлений приложения blog."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, QuerySet, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .constants import NUM_OF_POSTS_PER_PAGE
from .forms import CommentForm, EditProfileForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()


def get_filtered_posts(all_posts=None) -> QuerySet[Post]:
    """Возвращает QuerySet отфильтрованных записей блогов.

    Параметры:
            all_posts (bool): если True, то выбираются все записи блога
    """
    queryset = Post.objects.select_related(
        'author',
        'location',
        'category'
    )
    if not all_posts:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    return queryset


def get_paginated_posts(request, post_list: QuerySet[Post]) -> Paginator:
    """
    Возвращает разбитые на страницы записи блога.

    Параметры:
        post_list (QuerySet[Post]): QuerySet выбираемых записей блогов
    """
    paginator = Paginator(post_list, NUM_OF_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Обрабатывает запрос к главной странице 'Лента записей'."""
    post_list = (get_filtered_posts()
                 .annotate(comment_count=Count('comments'))
                 .order_by('-pub_date')
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
        get_filtered_posts(all_posts=True)
        .filter(
            Q(is_published=True)
            | (Q(is_published=False) & Q(author=request.user.id))
        ),
        pk=post_id
    )

    if ((not post.category.is_published or post.pub_date >= timezone.now())
            and post.author != request.user):
        return HttpResponse(status=404)

    context = {
        'form': CommentForm(),
        'comments': Comment.objects.filter(post=post_id),
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
        get_filtered_posts()
        .filter(category=category)
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
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
        get_filtered_posts(all_posts=True)
        .filter(
            Q(is_published=True)
            | (Q(is_published=False)
               & Q(author=request.user.id)
               ),
            author=profile.pk
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    context = {
        'profile': profile,
        'page_obj': get_paginated_posts(request, post_list)
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'blog/user.html', context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        # object = self.get_object()
        return self.get_object().author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):

    def get_initial(self):
        initial = super().get_initial()
        initial['pub_date'] = timezone.now().date()
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class PostUpdateView(OnlyAuthorMixin, PostMixin, UpdateView):

    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if (not request.user.is_authenticated
                or self.post_instance.author != self.request.user):
            return redirect(
                'blog:post_detail',
                post_id=self.post_instance.id
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):

    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context.update({
            'form': PostForm(instance=post_instance),
        })
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.comment.post.id}
        )

class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(
            Post,
            pk=self.kwargs['comment_id']
        )
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        form.instance.post = self.post_instance
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.post_instance.id}
        )


class CommentUpdateView(OnlyAuthorMixin, CommentMixin, UpdateView):

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.id = self.comment.id
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return super().dispatch(request, *args, **kwargs)
