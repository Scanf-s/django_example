from typing import Dict, TYPE_CHECKING

from django.db.models import Manager
from django.db.models.query import QuerySet

if TYPE_CHECKING:
    from book.models import Book

class BookManager(Manager):

    def get_all_books(self, request) -> QuerySet:
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

