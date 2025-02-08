from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from jwt_auth.models import Token
from tag.models import Tag
from user.models import User, UserRole


class TagTestCase(APITestCase):

    USER_USERNAME = "test"
    USER_EMAIL = "j9XeV@example.com"
    USER_PASSWORD = "123@1231@23@1231@23"

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

    def test_create_tag(self):
        response = self.client.post(path=reverse("tags"), data={"name": "test"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_tags(self):
        # Given
        bulk_tags = []
        for i in range(10):
            bulk_tags.append(Tag(name=f"tag-{i}"))
        Tag.objects.bulk_create(bulk_tags)

        # When
        response = self.client.get(path=reverse("tags"))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_get_tag_by_id(self):
        # Given
        bulk_tags = []
        for i in range(10):
            bulk_tags.append(Tag(name=f"tag-{i}"))
        Tag.objects.bulk_create(bulk_tags)

        # When
        response = self.client.get(path=reverse("tag_detail", kwargs={"tag_id": 1}))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), "tag-0")

    def test_update_tag_by_id(self):
        # Given
        tag: Tag = Tag.objects.create(name="test")

        # When
        response = self.admin_client.put(
            path=reverse("tag_detail", kwargs={"tag_id": 1}), data={"name": "update"}
        )

        # Then
        tag.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, "update")

    def test_update_with_invalid_user(self):
        # Given
        tag: Tag = Tag.objects.create(name="test")

        # When
        response = self.client.put(
            path=reverse("tag_detail", kwargs={"tag_id": 1}), data={"name": "update"}
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_tag_by_id(self):
        # Given
        tag: Tag = Tag.objects.create(name="test")

        # When
        response = self.admin_client.delete(
            path=reverse("tag_detail", kwargs={"tag_id": 1})
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.all().count(), 0)

    def test_delete_with_invalid_user(self):
        # Given
        tag: Tag = Tag.objects.create(name="test")

        # When
        response = self.client.delete(path=reverse("tag_detail", kwargs={"tag_id": 1}))

        # Then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        Tag.objects.all().delete()
        Token.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()
