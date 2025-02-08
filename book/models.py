from django.db import models

from book.managers.book_manager import BookManager
from common.models import TimeStampModel


class Book(TimeStampModel):
    book_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    stock = models.IntegerField()

    tags = models.ManyToManyField(
        to="tag.Tag", through="book.BookTag", related_name="books"
    )

    objects = BookManager()

    class Meta:
        db_table = "book"
        indexes = [
            models.Index(fields=["isbn"]),
        ]


class BookTag(models.Model):
    tag = models.ForeignKey(to="tag.Tag", on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(to="book.Book", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "book_tag"
        unique_together = ("tag", "book")
