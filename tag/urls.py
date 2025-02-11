from django.urls import path

from tag.views import TagDetailView, TagView

urlpatterns = [
    path("", TagView.as_view(), name="tags"),
    path("/<int:tag_id>", TagDetailView.as_view(), name="tag_detail"),
]
