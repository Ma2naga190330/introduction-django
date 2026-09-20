from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Activity, Certification, Skill


@login_required
def dashboard_view(request):
    context = {
        "activities": Activity.objects.all(),
        "certifications": Certification.objects.all(),
        "skills": Skill.objects.all(),
    }
    return render(request, "portfolio/dashboard.html", context)
