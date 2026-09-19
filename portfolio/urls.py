from django.urls import path

from .views import auth, public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
    path("login/", auth.login_view, name="login"),
]
