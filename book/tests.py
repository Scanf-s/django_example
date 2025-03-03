from typing import Any, Dict, List
from unittest.mock import patch

from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from book.models import Book
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

    @patch("book.views.cache.delete_pattern")
    def test_create_book(self, mock_cache_delete_pattern):
        response = self.client.post(
            path=reverse("books"),
            data={
                "title": "test",
                "author": "test",
                "isbn": "9788966260959",
                "stock": 1,
                "published_at": timezone.now().date(),
                "tags": [{"tag_id": 1}, {"tag_id": 2}],
            },
            format="json",
        )
        mock_cache_delete_pattern.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(book_id=1).exists())
        self.assertEqual(Book.objects.filter(tags__tag_id__in=[1, 2]).count(), 2)

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_cache_miss(self, mock_cache_get, mock_cache_set):
        # Given
        mock_cache_get.return_value = None
        bulk_books: List[Book] = []
        for i in range(10):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        books: QuerySet = Book.objects.filter(title__startswith="book-")
        tags: List[Tag] = [Tag.objects.get(tag_id=3), Tag.objects.get(tag_id=4)]

        for book in books:
            book.tags.set(tags)

        # When
        response = self.client.get(path=reverse("books"), format="json")  # Cache miss

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 10)
        mock_cache_set.assert_called_once()

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_cache_miss(self, mock_cache_get, mock_cache_set):
        # Given
        mock_cache_get.return_value = None
        bulk_books: List[Book] = []
        for i in range(10):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        books: QuerySet = Book.objects.filter(title__startswith="book-")
        tags: List[Tag] = [Tag.objects.get(tag_id=3), Tag.objects.get(tag_id=4)]

        for book in books:
            book.tags.set(tags)

        # When
        response = self.client.get(path=reverse("books"), format="json")  # Cache miss

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 10)
        mock_cache_set.assert_called_once()

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_cache_hit(self, mock_cache_get, mock_cache_set):
        # Given
        cached_data: Dict[str, Any] = {
            "count": 10,
            "next": None,
            "previous": None,
            "results": [
                {
                    "book_id": 10,
                    "isbn": "9788966260959",
                    "title": "book-9",
                    "author": "test",
                    "stock": 1,
                    "published_at": "2025-02-19",
                    "tags": [
                        {"tag_id": 3, "name": "tag-2"},
                        {"tag_id": 4, "name": "tag-3"},
                    ],
                },
                {
                    "book_id": 9,
                    "isbn": "9788966260959",
                    "title": "book-8",
                    "author": "test",
                    "stock": 1,
                    "published_at": "2025-02-18",
                    "tags": [
                        {"tag_id": 3, "name": "tag-2"},
                        {"tag_id": 4, "name": "tag-3"},
                    ],
                },
                {
                    "book_id": 1,
                    "isbn": "9788966260959",
                    "title": "book-0",
                    "author": "test",
                    "stock": 1,
                    "published_at": "2025-02-10",
                    "tags": [
                        {"tag_id": 3, "name": "tag-2"},
                        {"tag_id": 4, "name": "tag-3"},
                    ],
                },
            ],
        }
        # 캐시 hit 상황이므로 캐시에서 cached_data를 바로 반환하도록 설정
        mock_cache_get.return_value = cached_data

        # When
        response = self.client.get(path=reverse("books"), format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, cached_data)
        mock_cache_set.assert_not_called()

    def test_get_book_by_id(self):
        # Given
        bulk_books: List = []
        book_cnt: int = 3
        for i in range(book_cnt):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        # When
        response = self.client.get(path=reverse("book_detail", kwargs={"book_id": 1}))

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("title"), "book-0")

    @patch("book.views.cache.delete_pattern")
    def test_put_book_by_id(self, mock_cache_delete_pattern):
        # Given
        bulk_books: List = []
        book_cnt: int = 3
        for i in range(book_cnt):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        # When
        response = self.client.put(
            path=reverse("book_detail", kwargs={"book_id": 3}),
            data={
                "isbn": "9788111160959",
                "title": "update",
                "author": "test",
                "stock": 123,
                "published_at": timezone.now().date(),
                "tags": [{"tag_id": 3}, {"tag_id": 4}],
            },
            format="json",
        )

        # Then
        mock_cache_delete_pattern.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book: Book = Book.objects.filter(book_id=3).first()
        self.assertEqual(book.title, "update")
        self.assertEqual(book.tags.count(), 2)
        self.assertEqual(book.isbn, "9788111160959")
        self.assertEqual(book.author, "test")
        self.assertEqual(book.stock, 123)

    @patch("book.views.cache.delete_pattern")
    def test_delete_book_by_id(self, mock_cache_delete_pattern):
        # Given
        bulk_books: List = []
        book_cnt: int = 3
        for i in range(book_cnt):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        # When
        response = self.client.delete(
            path=reverse("book_detail", kwargs={"book_id": 1})
        )

        # Then
        mock_cache_delete_pattern.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.all().count(), book_cnt - 1)

    @patch("book.views.cache.delete_pattern")
    def test_patch_book_by_id(self, mock_cache_delete_pattern):
        # Given
        bulk_books = []
        for i in range(10):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        # When
        response = self.client.patch(
            path=reverse("book_detail", kwargs={"book_id": 3}),
            data={"title": "update"},
            format="json",
        )

        # Then
        mock_cache_delete_pattern.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Book.objects.filter(book_id=3).first().title, "update")

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_by_title_cache_miss(self, mock_cache_get, mock_cache_set):
        # Given
        mock_cache_get.return_value = None
        Book.objects.create(
            title="book-0", author="test", isbn="9788966260959", stock=1
        )
        Book.objects.create(
            title="123123book-0123123123", author="test", isbn="9788966260960", stock=1
        )
        Book.objects.create(
            title="asdf-1", author="test", isbn="9788964460959", stock=1
        )

        # When
        response = self.client.get(
            path=reverse("books"), query_params={"title": "book-0"}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)
        mock_cache_set.assert_called_once()

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_by_title_cache_hit(self, mock_cache_get, mock_cache_set):
        # Given
        cached_data: Dict[str, Any] = {
            "count": 10,
            "next": None,
            "previous": None,
            "results": [
                {
                    "book_id": 10,
                    "isbn": "9788966260959",
                    "title": "book-9",
                    "author": "test",
                    "stock": 1,
                    "published_at": "2025-02-19",
                    "tags": [
                        {"tag_id": 1, "tag_name": "tag-1"},
                        {"tag_id": 2, "tag_name": "tag-2"},
                    ],
                }
            ],
        }
        mock_cache_get.return_value = cached_data

        # When
        response = self.client.get(
            path=reverse("books"), query_params={"title": "book-0"}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, cached_data)
        mock_cache_set.assert_not_called()

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_by_author_cache_miss(self, mock_cache_get, mock_cache_set):
        # Given
        mock_cache_get.return_value = None
        Book.objects.create(
            title="book-0", author="test", isbn="9788966260959", stock=1
        )
        Book.objects.create(
            title="123123book-0123123123", author="asdf", isbn="9788966260960", stock=1
        )
        Book.objects.create(
            title="asdf-1", author="test", isbn="9788964460959", stock=1
        )

        # When
        response = self.client.get(
            path=reverse("books"), query_params={"author": "test"}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)
        mock_cache_set.assert_called_once()

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_by_tags_cache_miss(self, mock_cache_get, mock_cache_set):
        # Given
        mock_cache_get.return_value = None
        book1 = Book.objects.create(
            title="Book One",
            author="Author A",
            isbn="9788966260959",
            stock=5,
            published_at=timezone.now().date(),
        )
        book2 = Book.objects.create(
            title="Book Two",
            author="Author B",
            isbn="9788966260960",
            stock=5,
            published_at=timezone.now().date() + timezone.timedelta(days=1),
        )
        book3 = Book.objects.create(
            title="Book Three",
            author="Author C",
            isbn="9788966260961",
            stock=5,
            published_at=timezone.now().date() + timezone.timedelta(days=2),
        )

        tag1 = Tag.objects.get(tag_id=1)
        tag2 = Tag.objects.get(tag_id=2)
        tag3 = Tag.objects.get(tag_id=3)

        book1.tags.set([tag1, tag2])
        book2.tags.set([tag1])
        book3.tags.set([tag2, tag3])

        # When
        # tag-0과 tag-1을 AND 조건으로 필터링
        # GET 요청 시, query param으로 전달
        response = self.client.get(
            path=reverse("books"),
            data={"tag": ["1", "2"], "tag_option": "and"},
            format="json",
        )

        # Then
        # tag1, tag2를 모두 가진 Book1만 반환되어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)
        self.assertEqual(response.data.get("results")[0]["title"], "Book One")

        # When
        # tag-1 또는 tag-2를 OR 조건으로 필터링
        response = self.client.get(
            path=reverse("books"),
            data={"tag": ["1", "2"], "tag_option": "or"},
            format="json",
        )

        # Then
        # tag1 또는 tag2를 가지고 있는 책 3개가 모두 반환되어야함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 3)

        # When
        # tag-1만 지정한 경우, tag-1을 가지고 있는 Book One, Book Two만 반환되어야 함
        response = self.client.get(
            path=reverse("books"), data={"tag": 1}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)
        self.assertEqual(mock_cache_set.call_count, 3)

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_by_tags_cache_hit(self, mock_cache_get, mock_cache_set):
        # Given
        cached_data: Dict[str, Any] = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "book_id": 1,
                    "isbn": "9788966260959",
                    "title": "Book One",
                    "author": "Author A",
                    "stock": 5,
                    "published_at": "2025-02-10",
                    "tags": [
                        {"tag_id": 1, "name": "tag-0"},
                        {"tag_id": 2, "name": "tag-1"},
                    ],
                }
            ],
        }
        mock_cache_get.return_value = cached_data

        # When
        response = self.client.get(
            path=reverse("books"),
            data={"tag": ["1", "2"], "tag_option": "and"},
            format="json",
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)
        mock_cache_set.assert_not_called()

    @patch("book.views.cache.set")
    @patch("book.views.cache.get")
    def test_get_books_order_by_field_cache_miss(self, mock_cache_get, mock_cache_set):
        # Given
        mock_cache_get.return_value = None
        bulk_books = []
        for i in range(10):
            bulk_books.append(
                Book(
                    title=f"book-{i}",
                    author="test",
                    isbn="9788966260959",
                    stock=1,
                    published_at=timezone.now().date() + timezone.timedelta(days=i),
                )
            )
        Book.objects.bulk_create(bulk_books)

        # When
        # title 오름차순
        response = self.client.get(
            path=reverse("books"), query_params={"order_by": "title"}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data.get("results")[0]["title"]
            < response.data.get("results")[1]["title"]
        )

        # When
        # title 내림차순
        response = self.client.get(
            path=reverse("books"), query_params={"order_by": "-title"}, format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data.get("results")[0]["title"]
            > response.data.get("results")[1]["title"]
        )

        # When
        # published_at 오름차순
        response = self.client.get(
            path=reverse("books"),
            query_params={"order_by": "published_at"},
            format="json",
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data.get("results")[0]["published_at"]
            < response.data.get("results")[1]["published_at"]
        )

        # When
        # published_at 내림차순
        response = self.client.get(
            path=reverse("books"),
            query_params={"order_by": "-published_at"},
            format="json",
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.data.get("results")[0]["published_at"]
            > response.data.get("results")[1]["published_at"]
        )
        self.assertEqual(mock_cache_set.call_count, 4)

    def tearDown(self):
        Book.objects.all().delete()
        Token.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()
