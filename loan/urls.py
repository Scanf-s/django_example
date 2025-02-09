from django.urls import path

from loan.views import *

urlpatterns = [
    path("", LoanView.as_view(), name="loans"),
    path("/<int:loan_id>", LoanDetailView.as_view(), name="loan_detail"),
    path("/books/<int:book_id>", BookLoanView.as_view(), name="book_loans"),
]
