from django.urls import path, include

urlpatterns = [
    path('api/v1/token', include("jwt.urls")),
    path('api/v1/auth', include("user.urls.auth_urls")),
    path('api/v1/users', include("user.urls.user_urls")),
]
