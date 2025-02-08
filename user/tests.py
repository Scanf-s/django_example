from rest_framework.test import APIClient, APITestCase, force_authenticate
from django.urls import reverse
from rest_framework import status
from user.models import User

class UserTestCase(APITestCase):

    USER_EMAIL = "test@test.com"
    USER_PASSWORD = "123@1231@23@1231@23"
    USER_USERNAME = "test"

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username=self.USER_USERNAME, email=self.USER_EMAIL, password=self.USER_PASSWORD)
        self.client.force_authenticate(user=self.user)
        return super().setUp()

    def test_user_create(self):
        _email = "test2@test.com"
        response = self.client.post(
            path=reverse("user"),
            data={
                "email": _email,
                "password": self.USER_PASSWORD,
                "username": self.USER_USERNAME
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user: User = User.objects.filter(email=self.USER_EMAIL).first()
        self.assertEqual(user.username, self.USER_USERNAME)
        self.assertEqual(user.email, self.USER_EMAIL)

    def test_duplicate_user_create(self):
        response = self.client.post(
            path=reverse("user"),
            data={
                "email": self.USER_EMAIL,
                "password": self.USER_PASSWORD,
                "username": self.USER_USERNAME
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "ValidationError")

    def test_invalid_email_when_creating_user(self):
        response = self.client.post(
            path=reverse("user"),
            data={
                "email": "hahaha",
                "password": self.USER_PASSWORD,
                "username": self.USER_USERNAME
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "ValidationError")

    def test_invalid_password_when_creating_user(self):
        _email = "test2@test.com"
        response = self.client.post(
            path=reverse("user"),
            data={
                "email": _email,
                "password": "hahaha",
                "username": self.USER_USERNAME
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "ValidationError")


    def tearDown(self):
        User.objects.all().delete()
        return super().tearDown()
