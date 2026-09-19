from django.urls import path

from .views import activity, auth, certification, dashboard, public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("dashboard/", dashboard.dashboard_view, name="dashboard"),
    path("activities/new/", activity.activity_create_view, name="activity_create"),
    path("activities/<int:pk>/edit/", activity.activity_update_view, name="activity_update"),
    path("activities/<int:pk>/delete/", activity.activity_delete_view, name="activity_delete"),
    path("certifications/new/", certification.certification_create_view, name="certification_create"),
]
