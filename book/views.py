import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from book.models import Book, BookOrderFilterOption
from book.paginator import BookPagination
from book.serializers.book_create_serializer import BookCreateSerializer
from book.serializers.book_response_serializer import BookResponseSerializer
from book.serializers.book_update_serilaizer import BookUpdateSerializer
from common.exceptions import custom_exception_handler
from jwt_auth.authentication import JWTAuthentication
from tag.models import TagFilterOption

logger = logging.getLogger(__name__)


class BookView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_cache_key(self, query_params: Dict[str, str]) -> str:
        # query_params를 정렬된 JSON 문자열로 변환 후 MD5 해시를 사용해서 고유한 키 생성
        key_str = json.dumps(query_params, sort_keys=True)
        return f"book_key_{hashlib.md5(key_str.encode('utf-8')).hexdigest()}"

    @custom_exception_handler
    def get(self, request) -> Response:
        """
        도서관에 존재하는 모든 도서 리스트 조회
        """
        title: Optional[str] = request.query_params.get("title", None)
        author: Optional[str] = request.query_params.get("author", None)
        tag_ids: Optional[List[int]] = request.query_params.getlist("tag", None)
        tag_option: Optional[str] = request.query_params.get("tag_option", None)
        order_field: Optional[str] = request.query_params.get("order_by", None)
        page_size: Optional[int] = request.query_params.get("page_size", 100)

        if order_field and order_field not in BookOrderFilterOption.values:
            raise ValidationError("order_by value is invalid. please check API Docs")

        if len(tag_ids) >= 2 and tag_option is None:
            raise ValidationError(
                "tag_option is required when you filter books by tags"
            )

        if len(tag_ids) >= 2 and tag_option not in TagFilterOption.values:
            raise ValidationError("tag_option is invalid. please check API Docs")

        _query_params: Dict[str, str] = {
            "title": title,
            "author": author,
            "tag_ids": tag_ids,
            "tag_option": tag_option,
            "order_field": order_field,
            "page_size": page_size,
        }

        cache_key: Optional[str] = self.get_cache_key(_query_params)
        cached_data: str = cache.get(cache_key)
        if cached_data is not None:  # Cache Hit
            return Response(cached_data)

        if title or author or tag_ids:
            queryset: QuerySet = Book.objects.get_books(
                title=title,
                author=author,
                tag_ids=tag_ids,
                tag_option=tag_option,
                order_field=order_field,
            )
        else:
            queryset: QuerySet = Book.objects.get_all_books(order_field=order_field)

        paginator: BookPagination = BookPagination()
        paginated_queryset: QuerySet = paginator.paginate_queryset(queryset, request)
        serializer: BookResponseSerializer = BookResponseSerializer(
            instance=paginated_queryset, many=True
        )
        paginated_response: Any = paginator.get_paginated_response(
            data=serializer.data
        ).data
        cache.set(
            cache_key, paginated_response, timeout=180
        )  # 여기까지 넘어온 경우 Cache Miss이므로 해당 Cache key와 value에 대해서 Redis에 저장
        return paginator.get_paginated_response(data=serializer.data)

    @custom_exception_handler
    def post(self, request) -> Response:
        """
        도서 등록 API
        """
        serializer: BookCreateSerializer = BookCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete_pattern("book_key_*")
        return Response(status=status.HTTP_201_CREATED)


class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @custom_exception_handler
    def get(self, request, **kwargs) -> Response:
        """
        book_id로 도서 정보 조회 -> quantity 여부에 따라 대출 가능 여부 처리 가능
        """
        book: Book = Book.objects.filter(book_id=kwargs.get("book_id")).first()
        if not book:
            raise NotFound("Book not found")

        serializer: BookResponseSerializer = BookResponseSerializer(instance=book)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @custom_exception_handler
    def put(self, request, **kwargs) -> Response:
        """
        book_id로 도서 정보 수정
        """
        book: Book = Book.objects.filter(book_id=kwargs.get("book_id")).first()
        if not book:
            raise NotFound("Book not found")

        serializer: BookUpdateSerializer = BookUpdateSerializer(
            instance=book, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete_pattern("book_key_*")
        return Response(status=status.HTTP_200_OK)

    @custom_exception_handler
    def patch(self, request, **kwargs) -> Response:
        """
        book_id로 도서 정보 일부 수정
        """
        book: Book = Book.objects.filter(book_id=kwargs.get("book_id")).first()
        if not book:
            raise NotFound("Book not found")

        serializer: BookUpdateSerializer = BookUpdateSerializer(
            instance=book, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete_pattern("book_key_*")
        return Response(status=status.HTTP_200_OK)

    @custom_exception_handler
    def delete(self, request, **kwargs) -> Response:
        """
        book_id로 도서 정보 삭제
        """
        book: Book = Book.objects.filter(book_id=kwargs.get("book_id")).first()
        if not book:
            raise NotFound("Book not found")

        book.delete()
        cache.delete_pattern("book_key_*")
        return Response(status=status.HTTP_204_NO_CONTENT)
