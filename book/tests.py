from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from book.models import Book, Tag, BookTag
from jwt_auth.models import Token
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
            path=reverse("book"),
            data={
                "title": "test",
                "author": "test",
                "isbn": "test",
                "stock": 1,
                "tags": ["1", "2"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def tearDown(self):
        Book.objects.all().delete()
        Token.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()