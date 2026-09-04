import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from chores.models import UserProfile

@pytest.mark.django_db
def test_unauthenticated_redirect_to_login(client):
    response = client.get(reverse("dashboard"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))
    assert "next=" in response.url

@pytest.mark.django_db
def test_login_page_renders(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200
    assert "Roommate Log In" in response.content.decode("utf-8")
    assert "id_username" in response.content.decode("utf-8")

@pytest.mark.django_db
def test_login_success(client):
    user = User.objects.create_user(username="alex", password="password123")
    UserProfile.objects.create(user=user, total_points=15)

    response = client.post(reverse("login"), {
        "username": "alex",
        "password": "password123",
    })
    assert response.status_code == 302
    assert response.url == reverse("dashboard")

    # Following redirect or checking session
    dashboard_resp = client.get(reverse("dashboard"))
    assert dashboard_resp.status_code == 200

@pytest.mark.django_db
def test_login_invalid_credentials(client):
    response = client.post(reverse("login"), {
        "username": "wronguser",
        "password": "wrongpassword",
    })
    assert response.status_code == 200
    assert "Your username and password didn&#x27;t match" in response.content.decode("utf-8") or "didn't match" in response.content.decode("utf-8")

@pytest.mark.django_db
def test_logout_flow(client):
    user = User.objects.create_user(username="sam", password="password123")
    client.login(username="sam", password="password123")

    response = client.post(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("login")

    # Now trying to access protected route redirects to login
    protected_resp = client.get(reverse("dashboard"))
    assert protected_resp.status_code == 302
    assert protected_resp.url.startswith(reverse("login"))

@pytest.mark.django_db
def test_navigation_bar_authenticated_user_points(client):
    user = User.objects.create_user(username="taylor", password="password123")
    UserProfile.objects.create(user=user, total_points=42)
    client.login(username="taylor", password="password123")

    response = client.get(reverse("design_system_preview"))
    content = response.content.decode("utf-8")
    assert "taylor" in content
    assert "⭐ 42 pts" in content
    assert "Log out" in content
