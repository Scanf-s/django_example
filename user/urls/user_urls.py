from django.urls import path
from user.views.user_views import *

urlpatterns = [
    path("", UserView.as_view(), name="user"),
    path("/<str:user_id>", UserDetailView.as_view(), name="user"),
]
