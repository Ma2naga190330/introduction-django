from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import SkillForm
from ..models import Skill


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


@login_required
def skill_update_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = SkillForm(instance=skill)
    return render(request, "portfolio/skill_form.html", {"form": form, "skill": skill})
