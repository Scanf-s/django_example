from typing import TYPE_CHECKING, Dict, Optional, List

from django.db.models import Manager, Count, Q
from django.db.models.query import QuerySet
from tag.models import TagFilterOption
from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    from book.models import Book


class BookManager(Manager):

    def get_books(self, title: Optional[str], author: Optional[str], tag_ids: Optional[List[int]], tag_option: Optional[str]) -> QuerySet:
        queryset: QuerySet = self.all()
        if tag_ids:
            if len(tag_ids) == 1:
                queryset = queryset.filter(tags__tag_id=tag_ids[0])
            else:
                if tag_option == TagFilterOption.AND:
                    queryset = (
                        queryset.filter(tags__tag_id__in=tag_ids)
                        .annotate(match_count=Count("tags", filter=Q(tags__tag_id__in=tag_ids)))
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
        return queryset

    def get_all_books(self) -> QuerySet:
        return self.all()

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
