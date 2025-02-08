from rest_framework import serializers

from loan.models import Loan


class LoanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ["quantity"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")

        if self.instance.quantity != value:
            raise serializers.ValidationError("Quantity is not same. Invalid request")

        return value

    def update(self, instance: Loan, _) -> Loan:
        # 반납 처리
        instance.is_returned = True
        instance.save()
        return instance