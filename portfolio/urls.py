from django.urls import path

from .views import public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
]
