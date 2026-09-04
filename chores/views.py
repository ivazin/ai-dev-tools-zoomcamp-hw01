from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from chores.models import Chore

@login_required
def dashboard_view(request):
    tab = request.GET.get("tab", "my")
    user_profile = getattr(request.user, "profile", None)

    # Base querysets
    my_chores_qs = Chore.objects.filter(
        assignee=user_profile
    ).exclude(status=Chore.Status.COMPLETED).order_by("due_date")

    all_chores_qs = Chore.objects.exclude(
        status=Chore.Status.COMPLETED
    ).order_by("due_date")

    completed_chores_qs = Chore.objects.filter(
        status=Chore.Status.COMPLETED
    ).order_by("-completed_at")

    if tab == "all":
        chores = all_chores_qs
    elif tab == "completed":
        chores = completed_chores_qs
    else:
        tab = "my"
        chores = my_chores_qs

    context = {
        "active_tab": tab,
        "chores": chores,
        "my_chores_count": my_chores_qs.count(),
        "all_chores_count": all_chores_qs.count(),
        "completed_chores_count": completed_chores_qs.count(),
    }
    return render(request, "chores/dashboard.html", context)


@login_required
def claim_pool_view(request):
    chores = Chore.objects.filter(
        status=Chore.Status.CLAIMABLE,
        assignee__isnull=True,
    ).order_by("due_date")

    return render(request, "chores/claim_pool.html", {"chores": chores})


@login_required
def claim_chore_view(request, chore_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.http import HttpResponse
    from chores.services.chore_service import claim_chore

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    chore = get_object_or_404(Chore, id=chore_id)
    user_profile = getattr(request.user, "profile", None)

    if not user_profile:
        return HttpResponse('<div class="alert alert-danger">User profile not found.</div>', status=400)

    try:
        updated_chore = claim_chore(chore, user_profile)
    except ValueError as e:
        return HttpResponse(
            f'<div class="alert alert-danger" id="chore-{chore.id}">{str(e)}</div>',
            status=409,
        )

    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "chores/partials/chore_card.html",
            {"chore": updated_chore, "user": request.user},
        )

    return redirect("claim_pool")


@login_required
def complete_chore_view(request, chore_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.http import HttpResponse
    from chores.services.chore_service import complete_chore

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    chore = get_object_or_404(Chore, id=chore_id)
    user_profile = getattr(request.user, "profile", None)

    if not user_profile:
        return HttpResponse('<div class="alert alert-danger">User profile not found.</div>', status=400)

    # Permission check: assignee or staff
    if chore.assignee != user_profile and not request.user.is_staff:
        return HttpResponse(
            '<div class="alert alert-danger">Unauthorized: you can only complete chores assigned to you.</div>',
            status=403,
        )

    try:
        updated_chore = complete_chore(chore, user_profile)
    except ValueError as e:
        return HttpResponse(
            f'<div class="alert alert-danger" id="chore-{chore.id}">{str(e)}</div>',
            status=409,
        )

    if request.headers.get("HX-Request") == "true":
        card_html = render(
            request,
            "chores/partials/chore_card.html",
            {"chore": updated_chore, "user": request.user},
        ).content.decode("utf-8")

        # Include OOB swap for user points in navbar
        user_profile.refresh_from_db()
        oob_badge = f'<span class="badge badge-points" id="user-points-badge" hx-swap-oob="true">⭐ {user_profile.total_points} pts</span>'
        return HttpResponse(card_html + "\n" + oob_badge)

    return redirect("dashboard")


