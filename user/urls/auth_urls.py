from django.urls import path
from user.views.auth_views import *

urlpatterns = [
    path("/login", LoginView.as_view(), name="login"),
    path("/logout", LogoutView.as_view(), name="logout"),
]
