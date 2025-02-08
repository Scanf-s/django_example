import re

from rest_framework import serializers

from book.models import Book


class BookCreateSerializer(serializers.Serializer):
    isbn = serializers.CharField(max_length=13)
    title = serializers.CharField(max_length=50)
    author = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=1000)
    stock = serializers.IntegerField()
    tags = serializers.ListField(child=serializers.CharField(max_length=50))

    class Meta:
        model = Book
        fields = ['isbn', 'title', 'author', 'description', 'stock', 'tags']

    def validate_isbn(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("isbn cannot be empty")

        if not re.fullmatch(r'^[0-9]{13}$', value):
            raise serializers.ValidationError("invalid isbn")

        if Book.objects.filter(isbn=value).exists():
            raise serializers.ValidationError("Book isbn already exists (duplicate)")

        return value

    def validate_title(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("title cannot be empty")

        return value

    def validate_author(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("author cannot be empty")

        return value

    def validate_description(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("description cannot be empty")

        return value

    def validate_stock(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("stock cannot be empty")

        if value < 0:
            raise serializers.ValidationError("stock cannot be negative")

        return value

    def validate_tags(self, value):
        return value

    def create(self, validated_data):
        return Book.objects.create_book(request_body=validated_data)