# pages/urls.py
from django.template.defaulttags import url

import feed
from .views import HomePageView
from feed.views import PostUpdateView, PostListView, UserPostListView
from django.urls import path, include
from profiles import views as profiles_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", HomePageView.as_view(), name='home'),
    path('feed/', PostListView.as_view(), name='feed'),
    path('post/new/', feed.views.create_post, name='post-create'),
    path('post/<int:pk>/', feed.views.post_detail, name='post-detail'),
    path('like/', feed.views.like, name='post-like'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', feed.views.post_delete, name='post-delete'),
    path('search_posts/', feed.views.search_posts, name='search_posts'),
    path('user_posts/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('profiles/', profiles_views.users_list, name='users_list'),
    path('profiles/<slug>/', profiles_views.profile_view, name='profile_view'),
    path('friends/', profiles_views.friend_list, name='friend_list'),
    path('profiles/friend-request/send/<int:id>/', profiles_views.send_friend_request, name='send_friend_request'),
    path('profiles/friend-request/cancel/<int:id>/', profiles_views.cancel_friend_request, name='cancel_friend_request'),
    path('profiles/friend-request/accept/<int:id>/', profiles_views.accept_friend_request, name='accept_friend_request'),
    path('profiles/friend-request/delete/<int:id>/', profiles_views.delete_friend_request, name='delete_friend_request'),
    path('profiles/friend/delete/<int:id>/', profiles_views.delete_friend, name='delete_friend'),
    path('edit-profile/', profiles_views.edit_profile, name='edit_profile'),
    path('my-profile/', profiles_views.my_profile, name='my_profile'),
    path('search_users/', profiles_views.search_users, name='search_users'),
    path('register/', profiles_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
