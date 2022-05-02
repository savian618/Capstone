from django.shortcuts import render
from feed.models import Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from profiles.models import Profile, FriendRequest

User = get_user_model()


@login_required
def index_data(request, slug):
    p = Profile.objects.filter(slug=slug).first()
    u = p.user

    context = {
        'u': u,
    }

    return render(request, "/templates/index.html", context)
