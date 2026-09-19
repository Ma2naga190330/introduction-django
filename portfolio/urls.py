from django.urls import path

from .views import activity, auth, certification, dashboard, public, skill

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
    path("certifications/<int:pk>/edit/", certification.certification_update_view, name="certification_update"),
    path("certifications/<int:pk>/delete/", certification.certification_delete_view, name="certification_delete"),
    path("skills/new/", skill.skill_create_view, name="skill_create"),
    path("skills/<int:pk>/edit/", skill.skill_update_view, name="skill_update"),
]
