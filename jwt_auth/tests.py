from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User
from user.manager import UserManager

class JWTTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@test.com", password="123@1231@23@1231@23")
        self.user_manager = UserManager()
        return super().setUp
