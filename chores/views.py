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
