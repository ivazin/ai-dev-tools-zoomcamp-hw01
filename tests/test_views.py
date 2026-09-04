import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from chores.models import UserProfile, Chore

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


@pytest.mark.django_db
def test_dashboard_tabs_and_filtering(client):
    from django.utils import timezone
    import datetime

    user1 = User.objects.create_user(username="user1", password="pw")
    p1 = UserProfile.objects.create(user=user1)

    user2 = User.objects.create_user(username="user2", password="pw")
    p2 = UserProfile.objects.create(user=user2)

    now = timezone.now()

    # Chore 1: assigned to user1 (due in 2 days)
    c1 = Chore.objects.create(
        title="Dishes",
        points=2,
        status=Chore.Status.PENDING,
        assignee=p1,
        due_date=now + datetime.timedelta(days=2),
    )

    # Chore 2: assigned to user2 (due in 5 hours -> due soon)
    c2 = Chore.objects.create(
        title="Vacuum Living Room",
        points=3,
        status=Chore.Status.PENDING,
        assignee=p2,
        due_date=now + datetime.timedelta(hours=5),
    )

    # Chore 3: completed
    c3 = Chore.objects.create(
        title="Take out Trash",
        points=1,
        status=Chore.Status.COMPLETED,
        assignee=p1,
        completed_by=p1,
        due_date=now - datetime.timedelta(days=1),
        completed_at=now - datetime.timedelta(hours=1),
    )

    client.login(username="user1", password="pw")

    # Tab: My Chores (default)
    res_my = client.get(reverse("dashboard"))
    assert res_my.status_code == 200
    assert "Dishes" in res_my.content.decode("utf-8")
    assert "Vacuum Living Room" not in res_my.content.decode("utf-8")
    assert "Take out Trash" not in res_my.content.decode("utf-8")

    # Tab: All Household Chores
    res_all = client.get(reverse("dashboard") + "?tab=all")
    assert res_all.status_code == 200
    assert "Dishes" in res_all.content.decode("utf-8")
    assert "Vacuum Living Room" in res_all.content.decode("utf-8")
    assert "Due Soon" in res_all.content.decode("utf-8")
    assert "Take out Trash" not in res_all.content.decode("utf-8")

    # Tab: Completed Recently
    res_completed = client.get(reverse("dashboard") + "?tab=completed")
    assert res_completed.status_code == 200
    assert "Take out Trash" in res_completed.content.decode("utf-8")
    assert "Dishes" not in res_completed.content.decode("utf-8")


@pytest.mark.django_db
def test_dashboard_empty_states(client):
    user = User.objects.create_user(username="lonely", password="pw")
    UserProfile.objects.create(user=user)
    client.login(username="lonely", password="pw")

    res = client.get(reverse("dashboard") + "?tab=my")
    assert res.status_code == 200
    assert "No chores assigned to you!" in res.content.decode("utf-8")


@pytest.mark.django_db
def test_claim_pool_view_and_empty_state(client):
    from django.utils import timezone
    import datetime

    user = User.objects.create_user(username="claimer", password="pw")
    UserProfile.objects.create(user=user)
    client.login(username="claimer", password="pw")

    # Empty claim pool
    res = client.get(reverse("claim_pool"))
    assert res.status_code == 200
    assert "No chores in the claim pool right now!" in res.content.decode("utf-8")

    # Add claimable chore
    chore = Chore.objects.create(
        title="Mop Kitchen Floor",
        points=4,
        status=Chore.Status.CLAIMABLE,
        assignee=None,
        due_date=timezone.now() + datetime.timedelta(days=1),
    )

    res2 = client.get(reverse("claim_pool"))
    assert res2.status_code == 200
    assert "Mop Kitchen Floor" in res2.content.decode("utf-8")
    assert "Claim Chore" in res2.content.decode("utf-8")


@pytest.mark.django_db
def test_claim_chore_endpoint(client):
    from django.utils import timezone
    import datetime
    from chores.models import ChoreLog

    user = User.objects.create_user(username="sammy", password="pw")
    profile = UserProfile.objects.create(user=user)
    client.login(username="sammy", password="pw")

    chore = Chore.objects.create(
        title="Clean Microwave",
        points=2,
        status=Chore.Status.CLAIMABLE,
        assignee=None,
        due_date=timezone.now() + datetime.timedelta(days=1),
    )

    # Claim via HTMX
    res = client.post(
        reverse("claim_chore", kwargs={"chore_id": chore.id}),
        HTTP_HX_REQUEST="true",
    )
    assert res.status_code == 200
    assert "Clean Microwave" in res.content.decode("utf-8")
    assert "sammy" in res.content.decode("utf-8")

    # Check database
    chore.refresh_from_db()
    assert chore.assignee == profile
    assert chore.status == Chore.Status.PENDING

    # Check log
    log = ChoreLog.objects.filter(chore=chore, action=ChoreLog.Action.CLAIMED).first()
    assert log is not None
    assert log.user == profile

    # Attempting to claim again by another user fails with 409
    other_user = User.objects.create_user(username="other", password="pw")
    UserProfile.objects.create(user=other_user)
    client.login(username="other", password="pw")

    res_fail = client.post(
        reverse("claim_chore", kwargs={"chore_id": chore.id}),
        HTTP_HX_REQUEST="true",
    )
    assert res_fail.status_code == 409
    assert "Cannot claim chore" in res_fail.content.decode("utf-8")


