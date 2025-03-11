from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet, Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .constants import NUM_OF_POSTS_PER_PAGE
from .forms import CommentForm, EditProfileForm, PostForm
from .models import Category, Comment, Post


User = get_user_model()


def get_filtered_posts(all_posts=None) -> QuerySet[Post]:
    """Возвращает QuerySet отфильтрованных записей блогов."""
    if all_posts:
        return (Post.objects.select_related(
            'author',
            'location',
            'category',
        )
        )
    else:
        return (Post.objects.select_related(
            'author',
            'location',
            'category',
        )
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        )


def get_paginated_posts(request, post_list):
    paginator = Paginator(post_list, NUM_OF_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Обрабатывает запрос к главной странице 'Лента записей'."""
    post_list = get_filtered_posts().annotate(comment_count=Count('comments')).order_by('-pub_date')
    return render(
        request,
        'blog/index.html',
        {
            'page_obj': get_paginated_posts(request, post_list)
        },
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
        )
        ,pk=post_id
    )
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

@login_required
def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = (
        get_filtered_posts(all_posts=True)
        .filter(author=profile.pk)
        .filter(
            Q(is_published=True)
            | (Q(is_published=False) & Q(author=request.user.id))
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile,
            'page_obj': get_paginated_posts(request, post_list)}
    )


@login_required
def edit_profile(request):
    form = EditProfileForm(request.POST or None, instance=request.user)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request,'blog/user.html', context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['pub_date'] = timezone.now().date()
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.object.author.username})


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if (not request.user.is_authenticated
                or self.post_instance.author != self.request.user):
            return redirect('blog:post_detail', post_id=self.post_instance.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    # def get_success_url(self):
    #     return reverse_lazy('blog:profile', kwargs={'username': self.request.user})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context.update({
            'form': PostForm(instance=post_instance),
        })
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.object.author.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=self.kwargs['comment_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post = self.post_instance
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.post_instance.id})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.id = self.comment.id
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.comment.post.id})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.comment.post.id})