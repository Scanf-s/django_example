from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from jwt_auth.models import Token
from user.models import User, UserRole


class UserTestCase(APITestCase):

    USER_EMAIL = "test@test.com"
    USER_PASSWORD = "123@1231@23@1231@23"
    USER_USERNAME = "test"

    ADMIN_EMAIL = "admin@test.com"

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username=self.USER_USERNAME,
            email=self.USER_EMAIL,
            password=self.USER_PASSWORD,
        )
        self.client.force_authenticate(user=self.user)

        self.admin_client = APIClient()
        self.admin = User.objects.create_user(
            username=self.USER_USERNAME,
            email=self.ADMIN_EMAIL,
            password=self.USER_PASSWORD,
            role=UserRole.ADMIN,
        )
        self.admin_client.force_authenticate(user=self.admin)

        return super().setUp()

    def test_user_create(self):
        _email = "test2@test.com"
        response = self.client.post(
            path=reverse("user"),
            data={
                "email": _email,
                "password": self.USER_PASSWORD,
                "username": self.USER_USERNAME,
            },
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
                "username": self.USER_USERNAME,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "ValidationError")

    def test_invalid_email_when_creating_user(self):
        response = self.client.post(
            path=reverse("user"),
            data={
                "email": "hahaha",
                "password": self.USER_PASSWORD,
                "username": self.USER_USERNAME,
            },
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
                "username": self.USER_USERNAME,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "ValidationError")

    def test_login(self):
        response = self.client.post(
            path=reverse("login"),
            data={"email": str(self.USER_EMAIL), "password": str(self.USER_PASSWORD)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_invalid_login(self):
        response = self.client.post(
            path=reverse("login"),
            data={"email": str(self.USER_EMAIL), "password": "hahaha"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "ValidationError")

    def test_logout(self):
        # Given
        response = self.client.post(
            path=reverse("login"),
            data={"email": self.USER_EMAIL, "password": self.USER_PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token: str = response.data.get("refresh_token")

        # When
        response = self.client.post(
            path=reverse("logout"), data={"refresh_token": refresh_token}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Token.objects.filter(token=refresh_token).exists(), False)

    def test_invalid_user_logout(self):
        # Given
        invalid_client = APIClient()

        # When
        response = invalid_client.post(
            path=reverse("logout"), data={"refresh_token": "hahaha"}
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_users_with_admin_client(self):
        # When
        response = self.admin_client.get(path=reverse("user"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_with_user_client(self):
        # When
        response = self.client.get(path=reverse("user"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_my_info(self):
        # When
        response = self.client.get(
            path=reverse("user_detail", kwargs={"user_id": self.user.id})
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)
        self.assertIn("username", response.data)
        self.assertIn("id", response.data)

    def tearDown(self):
        Token.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()
