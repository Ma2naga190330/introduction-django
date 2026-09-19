from django.shortcuts import render

from ..models import Activity, Certification, Skill


def profile_view(request):
    context = {
        "activities": Activity.objects.all(),
        "certifications": Certification.objects.all(),
        "skills": Skill.objects.all(),
    }
    return render(request, "portfolio/profile.html", context)
