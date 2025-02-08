from django.db.models.query import QuerySet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from book.models import Book
from book.serializers.book_create_serializer import BookCreateSerializer
from book.serializers.book_response_serializer import BookResponseSerializer
from common.exceptions import exception_handler
from jwt.authentication import JWTAuthentication

@exception_handler
class BookView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """
        도서관에 존재하는 모든 도서 리스트 조회
        """
        queryset: QuerySet = Book.objects.get_all_books()
        serializer: BookResponseSerializer = BookResponseSerializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        도서 등록 API
        """
        serializer: BookCreateSerializer = BookCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
