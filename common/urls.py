from django.urls import path

from common.views import HealthView

urlpatterns = [
    path("", HealthView.as_view(), name="health"),
]