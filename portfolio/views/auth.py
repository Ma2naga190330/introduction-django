from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("portfolio:dashboard")
        error = "ユーザー名またはパスワードが正しくありません。"
    return render(request, "portfolio/login.html", {"error": error})


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("portfolio:profile")
