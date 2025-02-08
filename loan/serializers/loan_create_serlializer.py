from django.db import transaction
from rest_framework import serializers

from book.models import Book
from loan.models import Loan


class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["book", "quantity"]

    def validate(self, attrs):
        book: Book = attrs.get("book")
        quantity: int = attrs.get("quantity")
        if book.stock < quantity:
            raise serializers.ValidationError("Not enough stock")
        return attrs

    @transaction.atomic
    def create(self, validated_data) -> Loan:
        new_loan: Loan = Loan.objects.create_new_loan(
            user=self.context.get("user"),
            book=self.context.get("book"),
            **validated_data
        )

        Book.objects.update_quantity(
            book_id=new_loan.book.book_id, quantity=new_loan.quantity, is_decrease=True
        )
        return new_loan
