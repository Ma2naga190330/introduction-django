from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import ActivityForm


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
