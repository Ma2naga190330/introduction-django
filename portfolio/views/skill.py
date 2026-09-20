from django.contrib import messages
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
            messages.success(request, "スキルを登録しました。")
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
            messages.success(request, "スキルを更新しました。")
            return redirect("portfolio:dashboard")
    else:
        form = SkillForm(instance=skill)
    return render(request, "portfolio/skill_form.html", {"form": form, "skill": skill})


@login_required
def skill_delete_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            skill.delete()
            messages.success(request, "スキルを削除しました。")
        return redirect("portfolio:dashboard")
    return render(request, "portfolio/skill_confirm_delete.html", {"skill": skill})
