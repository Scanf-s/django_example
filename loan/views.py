from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from book.models import Book
from loan.models import Loan
from loan.serializers.loan_create_serlializer import LoanCreateSerializer
from loan.serializers.loan_response_serializer import LoanResponseSerializer
from loan.serializers.loan_update_serializer import LoanUpdateSerializer
from user.models import User, UserRole
from jwt_auth.authentication import JWTAuthentication
from rest_framework.exceptions import NotFound

class LoanView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request) -> Response:
        if request.user.role == UserRole.ADMIN:
            loans: QuerySet = Loan.objects.all()
        else:
            loans: QuerySet = Loan.objects.filter(user=request.user)
        serializer: LoanResponseSerializer = LoanResponseSerializer(instance=loans, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        user: User = request.user
        book: Book = Book.objects.filter(book_id=request.data.pop("book_id", None)).first()
        if not book:
            raise NotFound("Invalid book id")

        serializer: LoanCreateSerializer = LoanCreateSerializer(data=request.data, context={"user": user, "book": book})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class LoanDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, **kwargs) -> Response:
        loan: Loan = Loan.objects.filter(loan_id=kwargs.get("loan_id")).first()
        if not loan:
            raise NotFound("Loan not found")

        serializer: LoanResponseSerializer = LoanResponseSerializer(instance=loan)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        """
        대출 반납 시 사용하는 API (대출 상태 변경)
        """
        loan: Loan = Loan.objects.filter(loan_id=kwargs.get("loan_id"), is_returned=False).first()
        if not loan:
            raise NotFound("Invalid loan id or This loan has already been returned")

        serializer: LoanUpdateSerializer = LoanUpdateSerializer(instance=loan, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class BookLoanView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, **kwargs) -> Response:
        book: Book = Book.objects.filter(book_id=kwargs.get("book_id")).first()
        if not book:
            raise NotFound("Invalid book id")

        loans: QuerySet = Loan.objects.filter(book=book)
        serializer: LoanResponseSerializer = LoanResponseSerializer(instance=loans, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
