from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

def design_system_preview(request):
    return render(request, "design_system_preview.html")

@login_required
def placeholder_view(request):
    return HttpResponse("OK")

from chores.views import dashboard_view

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("design-system-preview/", design_system_preview, name="design_system_preview"),
    path("", dashboard_view, name="dashboard"),
    path("pool/", placeholder_view, name="claim_pool"),

    path("leaderboard/", placeholder_view, name="leaderboard"),
    path("create/", placeholder_view, name="chore_create"),
    path("profile/", placeholder_view, name="profile"),
]

