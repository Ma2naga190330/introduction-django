from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CertificationForm
from ..models import Certification


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


@login_required
def certification_update_view(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == "POST":
        form = CertificationForm(request.POST, instance=certification)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = CertificationForm(instance=certification)
    return render(
        request, "portfolio/certification_form.html", {"form": form, "certification": certification}
    )


@login_required
def certification_delete_view(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            certification.delete()
        return redirect("portfolio:dashboard")
    return render(
        request, "portfolio/certification_confirm_delete.html", {"certification": certification}
    )
