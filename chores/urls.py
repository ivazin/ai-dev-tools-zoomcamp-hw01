from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse

def design_system_preview(request):
    return render(request, "design_system_preview.html")

def placeholder_view(request):
    return HttpResponse("OK")

urlpatterns = [
    path("design-system-preview/", design_system_preview, name="design_system_preview"),
    path("", placeholder_view, name="dashboard"),
    path("pool/", placeholder_view, name="claim_pool"),
    path("leaderboard/", placeholder_view, name="leaderboard"),
    path("create/", placeholder_view, name="chore_create"),
    path("profile/", placeholder_view, name="profile"),
    path("login/", placeholder_view, name="login"),
    path("logout/", placeholder_view, name="logout"),
]
