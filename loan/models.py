from django.db import models

from common.models import TimeStampModel
from loan.manager import LoanManager


class Loan(TimeStampModel):
    loan_id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey("book.Book", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_returned = models.BooleanField(default=False)

    objects = LoanManager()

    class Meta:
        db_table = "loan"
