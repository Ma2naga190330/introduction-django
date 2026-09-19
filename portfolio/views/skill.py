from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import SkillForm


@login_required
def skill_create_view(request):
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = SkillForm()
    return render(request, "portfolio/skill_form.html", {"form": form})
