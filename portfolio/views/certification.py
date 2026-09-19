from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import CertificationForm


@login_required
def certification_create_view(request):
    if request.method == "POST":
        form = CertificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = CertificationForm()
    return render(request, "portfolio/certification_form.html", {"form": form})
