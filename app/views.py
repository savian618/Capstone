import json

from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from ct.settings import LOGIN_REDIRECT_URL
from profiles.models import Profile


class HomePageView(TemplateView):
    template_name = "main.html"
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(LOGIN_REDIRECT_URL)
        return super(HomePageView, self).dispatch(request, *args, **kwargs)

def get_context_data(request):
    context = {}
    queryset = Profile.objects.all()
    names = [p.headline for p in queryset]
    names.extend([p.pub_date for p in queryset])
    context['names'] = json.dumps(names)
    return render(request, 'index.html', context)
