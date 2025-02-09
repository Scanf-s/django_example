import random
from typing import List, Optional

from django.db.models.query import QuerySet
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from book.models import Book
from jwt_auth.models import Token
from loan.models import Loan
from tag.models import Tag
from user.models import User, UserRole


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

        self.admin = User.objects.create_user(
            username=self.USER_USERNAME,
            email="admin@test.com",
            password=self.USER_PASSWORD,
            role=UserRole.ADMIN,
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)

        bulk_tags: List = []
        for i in range(10):
            tag: Tag = Tag(name=f"tag-{i}")
            bulk_tags.append(tag)
        Tag.objects.bulk_create(bulk_tags)

        bulk_books: List = []
        for i in range(3):
            bulk_books.append(
                Book(title=f"book-{i}", author="test", isbn="9788966260959", stock=1)
            )
        Book.objects.bulk_create(bulk_books)

        books: QuerySet = Book.objects.all()
        for book in books:
            book.tags.set(
                [
                    Tag.objects.get(tag_id=random.randint(1, 3)),
                    Tag.objects.get(tag_id=random.randint(4, 6)),
                    Tag.objects.get(tag_id=random.randint(7, 9)),
                ]
            )

        return super().setUp()

    def test_create_loan(self):
        book: Book = Book.objects.filter(book_id=1).first()
        current_book_stock: int = book.stock
        request_quantity: int = book.stock
        response = self.client.post(
            path=reverse("loans"),
            data={"book_id": 1, "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        loan: Optional[Loan] = Loan.objects.filter(user=self.user, book_id=1).first()
        self.assertIsNotNone(loan)
        self.assertEqual(loan.quantity, 1)
        self.assertEqual(loan.is_returned, False)

        book.refresh_from_db()
        self.assertEqual(book.stock, current_book_stock - request_quantity)

    def test_create_loan_with_invalid_book_id(self):
        response = self.client.post(
            path=reverse("loans"),
            data={"book_id": 123, "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_loan_with_over_available_stock(self):
        response = self.client.post(
            path=reverse("loans"),
            data={"book_id": 1, "quantity": 123},
            format="json",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_loans_by_user(self):
        # Given
        Loan.objects.create(user=self.user, book_id=1, quantity=1)

        # When
        response = self.client.get(path=reverse("loans"), format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("loan_id", response.data[0])
        self.assertIn("user", response.data[0])
        self.assertIn("book", response.data[0])
        self.assertIn("quantity", response.data[0])
        self.assertIn("is_returned", response.data[0])

    def test_get_loans_by_admin(self):
        # Given
        Loan.objects.create(
            user=self.user, book_id=1, quantity=1
        )  # 본인게 아니어도 보여야함
        Loan.objects.create(user=self.admin, book_id=2, quantity=3)

        # When
        response = self.admin_client.get(path=reverse("loans"), format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_loan_by_loan_id(self):
        # Given
        loan: Loan = Loan.objects.create(user=self.user, book_id=1, quantity=1)

        # When
        response = self.client.get(
            path=reverse("loan_detail", kwargs={"loan_id": loan.loan_id}), format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("loan_id", response.data)
        self.assertIn("user", response.data)
        self.assertIn("book", response.data)
        self.assertIn("quantity", response.data)
        self.assertIn("is_returned", response.data)

    def test_check_in_book(self):
        """
        대출 반납 테스트
        """
        # Given
        loan: Loan = Loan.objects.create(user=self.user, book_id=1, quantity=1)
        book: Book = Book.objects.filter(book_id=1).first()
        current_book_stock: int = book.stock - loan.quantity
        book.save()

        # When
        response = self.client.patch(
            path=reverse("loan_detail", kwargs={"loan_id": loan.loan_id}),
            data={"quantity": loan.quantity},
            format="json",
        )

        # Then
        loan.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(loan.is_returned, True)
        self.assertEqual(book.stock, current_book_stock + loan.quantity)

    def test_get_loans_by_book_id(self):
        """
        특정 도서 (book_id)의 모든 대출 정보 조회
        """
        # Given
        book: Book = Book.objects.create(
            title="hello python", author="test", isbn="1231231231231", stock=100
        )
        for i in range(50):
            Loan.objects.create(user=self.user, book_id=book.book_id, quantity=1)

        self.assertEqual(Book.objects.filter(title="hello python").count(), 1)
        self.assertEqual(Loan.objects.filter(book_id=book.book_id).count(), 50)

        # When
        response = self.client.get(
            path=reverse("book_loans", kwargs={"book_id": book.book_id}), format="json"
        )

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 50)

    def tearDown(self):
        Book.objects.all().delete()
        Token.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()
