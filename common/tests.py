from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class CommonTestCase(APITestCase):

    def setUp(self):
        return super().setUp()

    def test_health_check(self):
        response = self.client.get(path=reverse("health"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
