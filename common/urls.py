from django.urls import path

from common.views import HealthView

urlpatterns = [
    path("/health-check", HealthView.as_view(), name="health"),
]
