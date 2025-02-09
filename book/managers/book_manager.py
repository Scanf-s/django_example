from typing import TYPE_CHECKING, Dict, List, Optional

from django.db.models import Count, Manager, Q
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError

from tag.models import TagFilterOption

if TYPE_CHECKING:
    from book.models import Book


class BookManager(Manager):

    def get_books(
        self,
        title: Optional[str],
        author: Optional[str],
        tag_ids: Optional[List[int]],
        tag_option: Optional[str],
        order_field: Optional[str],
    ) -> QuerySet:
        queryset: QuerySet = self.all()
        if tag_ids:
            if len(tag_ids) == 1:
                queryset = queryset.filter(tags__tag_id=tag_ids[0])
            else:
                if tag_option == TagFilterOption.AND:
                    queryset = (
                        queryset.filter(tags__tag_id__in=tag_ids)
                        .annotate(
                            match_count=Count(
                                "tags", filter=Q(tags__tag_id__in=tag_ids)
                            )
                        )
                        .filter(match_count=len(tag_ids))
                    )
                elif tag_option == TagFilterOption.OR:
                    queryset = queryset.filter(tags__tag_id__in=tag_ids).distinct()
                else:
                    raise ValidationError("Invalid tag_option")
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        if order_field:
            if order_field.startswith("-"):
                queryset = queryset.order_by(order_field)
            else:
                queryset = queryset.order_by(order_field)
        return queryset.order_by("-created_at")  # 기본 정렬 옵션

    def get_all_books(self, order_field: Optional[str]) -> QuerySet:
        return (
            self.all().order_by(order_field)
            if order_field
            else self.all().order_by("-created_at")
        )

    def create_book(self, request_body: Dict[str, str]) -> QuerySet:
        return self.create(**request_body)

    def update_quantity(self, book_id: int, quantity: int, is_decrease: bool) -> None:
        """
        is_decrease : True인경우, 대출 -> quantity 차감
        is_decrease : False인경우, 반납 -> quantity 증가
        """
        target: Book = self.filter(book_id=book_id).first()
        if is_decrease:
            target.stock -= quantity
        else:
            target.stock += quantity
        target.save()
