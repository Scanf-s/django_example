from django.urls import path
from jwt.views import *

urlpatterns = [
    path("/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
