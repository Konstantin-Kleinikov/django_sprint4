from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        #views.delete_post,
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:comment_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        views.user_profile,
        name='profile'
    ),
    path(
        'profile/',
        views.edit_profile,
        name='edit_profile'
    ),
    path('',
         views.index,
         name='index'
    ),
]
