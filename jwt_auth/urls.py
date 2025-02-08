from django.urls import path

from jwt_auth.views import *

urlpatterns = [
    path("/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
