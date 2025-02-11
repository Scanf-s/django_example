from django.urls import include, path

urlpatterns = [
    path("api/v1/token", include("jwt_auth.urls")),
    path("api/v1/auth", include("user.urls.auth_urls")),
    path("api/v1/users", include("user.urls.user_urls")),
    path("api/v1/books", include("book.urls")),
    path("api/v1/tags", include("tag.urls")),
    path("api/v1/loans", include("loan.urls")),
    path("api/v1/health", include("common.urls")),
]
