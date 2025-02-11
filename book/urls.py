from django.urls import path

from book.views import *

urlpatterns = [
    path("", BookView.as_view(), name="books"),
    path("/<int:book_id>", BookDetailView.as_view(), name="book_detail"),
]
