from typing import TYPE_CHECKING, Any

from django.db.models import Manager

from book.models import Book
from user.models import User

if TYPE_CHECKING:
    from loan.models import Loan


class LoanManager(Manager):

    def create_new_loan(self, user: User, book: Book, **kwargs) -> "Loan":
        loan: "Loan" = self.create(user=user, book=book, **kwargs)
        return loan
