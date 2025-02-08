from rest_framework import serializers

from loan.models import Loan


class LoanResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["loan_id", "user", "book", "quantity", "is_returned"]
