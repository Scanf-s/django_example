from django.urls import path

from tag.views import TagView, TagDetailView

urlpatterns = [
    path("", TagView.as_view(), name="tags"),
    path("/<int:tag_id>", TagDetailView.as_view(), name="tag_detail"),
]