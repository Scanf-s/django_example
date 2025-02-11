from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from book.models import Book
from loan.models import Loan


class LoanCreateSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField()

    class Meta:
        model = Loan
        fields = ["book_id", "quantity"]

    def validate(self, attrs):
        book: Book = Book.objects.filter(book_id=attrs.get("book_id")).first()
        if not book:
            raise NotFound("Invalid book id")

        quantity: int = attrs.get("quantity")
        if book.stock < quantity:
            raise serializers.ValidationError("Not enough stock")

        attrs["book"] = book
        return attrs

    @transaction.atomic
    def create(self, validated_data) -> Loan:
        new_loan: Loan = Loan.objects.create_new_loan(
            user=self.context.get("user"), **validated_data
        )

        Book.objects.update_quantity(
            book_id=new_loan.book.book_id, quantity=new_loan.quantity, is_decrease=True
        )
        return new_loan
