from django.urls import path

from .views import activity, auth, dashboard, public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("dashboard/", dashboard.dashboard_view, name="dashboard"),
    path("activities/new/", activity.activity_create_view, name="activity_create"),
]
