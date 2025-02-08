from typing import List

from django.db.models.query import QuerySet
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from book.models import Book, BookTag
from jwt_auth.models import Token
from tag.models import Tag
from user.models import User


class BookTestCase(APITestCase):

    USER_EMAIL = "test@test.com"
    USER_PASSWORD = "123@1231@23@1231@23"
    USER_USERNAME = "test"

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username=self.USER_USERNAME,
            email=self.USER_EMAIL,
            password=self.USER_PASSWORD,
        )
        self.client.force_authenticate(user=self.user)

        bulk_tags = []
        for i in range(10):
            tag: Tag = Tag(name=f"tag-{i}")
            bulk_tags.append(tag)
        Tag.objects.bulk_create(bulk_tags)
        return super().setUp()

    def test_create_book(self):
        response = self.client.post(
            path=reverse("books"),
            data={
                "title": "test",
                "author": "test",
                "isbn": "9788966260959",
                "stock": 1,
                "tags": [{"tag_id": 1}, {"tag_id": 2}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(book_id=1).exists())
        self.assertEqual(Book.objects.filter(tags__tag_id__in=[1, 2]).count(), 2)

    def test_get_books(self):
        # Given
        bulk_books = []
        for i in range(10):
            bulk_books.append(
                Book(title=f"book-{i}", author="test", isbn="9788966260959", stock=1)
            )
        Book.objects.bulk_create(bulk_books)

        books: QuerySet = Book.objects.filter(title__startswith="book-")
        tags: List[Tag] = [Tag.objects.get(tag_id=3), Tag.objects.get(tag_id=4)]

        for book in books:
            book.tags.set(tags)

        # When
        response = self.client.get(path=reverse("books"), format="json")
        print(response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def tearDown(self):
        Book.objects.all().delete()
        Token.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()
