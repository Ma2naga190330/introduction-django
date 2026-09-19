from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ActivityForm
from ..models import Activity


@login_required
def activity_create_view(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = ActivityForm()
    return render(request, "portfolio/activity_form.html", {"form": form})


@login_required
def activity_update_view(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = ActivityForm(instance=activity)
    return render(request, "portfolio/activity_form.html", {"form": form, "activity": activity})
