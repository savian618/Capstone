from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from requests import post

from .forms import NewCommentForm, NewPostForm
from django.views.generic import ListView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comments, Like
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from dal import autocomplete
from profiles.models import Profile, FriendRequest
import random


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed/home.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            liked = [i for i in Post.objects.all() if Like.objects.filter(user=self.request.user, post=i)]
            user = get_object_or_404(User, username=self.request.user)
            p = user.profile
            friends = p.friends.all()
            sent = FriendRequest.objects.filter(from_user=p.user)
            f_list = list(friends)
            s_list = list(sent)
            f_list = [x.user for x in f_list]
            s_list = [x.to_user for x in s_list]
            long = Profile.objects.exclude(user=self.request.user)
            users = long.exclude(user__in=f_list).exclude(user__in=s_list)
            context['users'] = users
            context['liked_post'] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        p = user.profile
        friends = p.friends.all()
        f_list = list(friends)
        f_list = [x.user for x in f_list]
        combined_q = Post.objects.filter(user_name__in=f_list) | Post.objects.filter(user_name=user)
        return combined_q.order_by('-date_posted')


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        liked = [i for i in Post.objects.filter(user_name=user) if Like.objects.filter(user=self.request.user, post=i)]
        context['liked_post'] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(user_name=user).order_by('-date_posted')


class ExploreListView(ListView):
    model = Post
    template_name = 'feed/explore.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ExploreListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            liked = [i for i in Post.objects.all() if Like.objects.filter(user=self.request.user, post=i)]
            context['liked_post'] = liked
        return context


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    is_liked = Like.objects.filter(user=user, post=post)
    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.post = post
            data.username = user
            data.save()
            return redirect('post-detail', pk=pk)
    else:
        form = NewCommentForm()
    return render(request, 'feed/post_detail.html', {'post': post, 'is_liked': is_liked, 'form': form})


@login_required
def create_post(request):
    user = request.user
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_name = user
            data.save()
            messages.success(request, f'Posted Successfully')
            return redirect('feed')
    else:
        form = NewPostForm()
    return render(request, 'feed/create_post.html', {'form': form})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['description', 'pic', 'tags']
    template_name = 'feed/create_post.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user_name:
            return True
        return False


@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user == post.user_name:
        Post.objects.get(pk=pk).delete()
    return redirect('feed')


@login_required
def search_posts(request):
    query = request.GET.get('q')
    object_list = Post.objects.filter(tags__icontains=query)
    liked = [i for i in object_list if Like.objects.filter(user=request.user, post=i)]
    context = {
        'posts': object_list,
        'liked_post': liked
    }
    return render(request, "feed/search_posts.html", context)


@login_required
def like(request, pk):
    post = Post.objects.get(pk=pk)
    user = request.user
    like = Like.objects.filter(user=user, post=post)
    if like:
        like.delete()
    else:
        Like.objects.create(user=user, post=post)

    return redirect('feed')


@login_required
def users_list(request):
    users = Profile.objects.exclude(user=request.user)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    my_friends = request.user.profile.friends.all()
    sent_to = []
    friends = []
    for user in my_friends:
        friend = user.friends.all()
        for f in friend:
            if f in friends:
                friend = friend.exclude(user=f.user)
        friends += friend
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    if request.user.profile in friends:
        friends.remove(request.user.profile)
    random_list = random.sample(list(users), min(len(list(users)), 10))
    for r in random_list:
        if r in friends:
            random_list.remove(r)
    friends += random_list
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    for se in sent_friend_requests:
        sent_to.append(se.to_user)
    context = {
        'users': friends,
        'sent': sent_to
    }
    return render(request, "feed/home.html", context)


@login_required
def liked_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    likes = Like.objects.filter(post=post)
    my_friends = request.user.profile.friends.all()
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    received_friend_requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'feed/likes.html', {'u': request.user, 'post': post, 'likes': likes, 'users': my_friends, 'sent': sent_friend_requests, 'receive': received_friend_requests})
