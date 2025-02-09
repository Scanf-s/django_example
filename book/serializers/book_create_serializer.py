import logging
import re
from typing import List

from rest_framework import serializers

from book.models import Book
from tag.models import Tag
from tag.serializers.tag_serializer import TagSerializer

logger = logging.getLogger(__name__)


class BookCreateSerializer(serializers.ModelSerializer):
    isbn = serializers.CharField(max_length=13)
    title = serializers.CharField(max_length=50)
    author = serializers.CharField(max_length=50)
    stock = serializers.IntegerField()
    published_at = serializers.DateField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Book
        fields = ["isbn", "title", "author", "stock", "published_at", "tags"]

    def validate_isbn(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("isbn cannot be empty")

        if not re.fullmatch(r"^[0-9]{13}$", value):
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

    def validate_stock(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("stock cannot be empty")

        if value < 0:
            raise serializers.ValidationError("stock cannot be negative")

        return value

    def valudate_published_at(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("published_at cannot be empty")

        return value

    def create(self, validated_data):
        tag_data: List = validated_data.pop("tags", None)
        book: Book = Book.objects.create_book(request_body=validated_data)

        for tag_dict in tag_data:
            tag_id: int = tag_dict.get("tag_id")
            tag, _ = Tag.objects.get_or_create(tag_id=tag_id)
            book.tags.add(tag)

        return book
