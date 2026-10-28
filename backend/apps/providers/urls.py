from django.urls import path
from apps.providers.views import HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="route-health"),
]