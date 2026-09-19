from django.urls import path

from .views import auth, dashboard, public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("dashboard/", dashboard.dashboard_view, name="dashboard"),
]
