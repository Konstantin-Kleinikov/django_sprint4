"""Вспомогательные функции для приложения blog."""
from typing import Any

from django.core.paginator import Page, Paginator
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from .constants import NUM_OF_POSTS_PER_PAGE
from .models import Post


def get_filtered_posts(
        request,
        all_posts=None,
        annotate=None
) -> QuerySet[Post]:
    """Возвращает QuerySet отфильтрованных записей блогов.

    Параметры:
            all_posts (bool): если True, то выбираются все записи блога
            annotate (bool): если True, выполняется подсчет кол-ва комментариев
    """
    queryset = Post.objects.select_related(
        'author',
        'location',
        'category'
    )
    if all_posts:
        queryset = queryset.exclude(
            ~Q(author=request.user.id)
            & (
                Q(is_published=False)
                | Q(category__is_published=False)
                | Q(pub_date__gt=timezone.now())
            )
        )
    else:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if annotate:
        queryset = queryset.annotate(comment_count=Count('comments'))
        queryset = queryset.order_by('-pub_date')
    return queryset


def get_paginated_posts(request, post_list: QuerySet[Post]) -> Page[Any]:
    """
    Возвращает разбитые на страницы записи блога.

    Параметры:
        post_list (QuerySet[Post]): QuerySet выбираемых записей блогов
    """
    paginator = Paginator(post_list, NUM_OF_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
