from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user.models import User
from user.manager import UserManager

class JWTTestCase(APITestCase):

    USER_EMAIL = "test@test.com"
    USER_PASSWORD = "123@1231@23@1231@23"
    USER_USERNAME = "test"

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username=self.USER_USERNAME, email=self.USER_EMAIL, password=self.USER_PASSWORD)
        self.client.force_authenticate(user=self.user)
        return super().setUp()

    def test_refresh_token(self):
        response = self.client.post(
            path=reverse("login"),
            data={
                "email": self.USER_EMAIL,
                "password": self.USER_PASSWORD
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token: str = response.data.get("refresh_token")

        response = self.client.post(
            path=reverse("refresh"),
            data={
                "refresh_token": refresh_token
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
