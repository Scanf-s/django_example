import re
from typing import List

from rest_framework import serializers

from book.models import Book, Tag


class BookUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ["isbn", "title", "author", "description", "stock", "tags"]

    def validate_isbn(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("isbn cannot be empty")

        if not re.fullmatch(r"^[0-9]{13}$", value):
            raise serializers.ValidationError("invalid isbn")

        if (
            Book.objects.filter(isbn=value)
            .exclude(book_id=self.instance.book_id)
            .exists()
        ):
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

    def update(self, instance, validated_data):
        tags: List = validated_data.pop("tags", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if tags is not None:
            # 기존 태그 전부 제거 후 새로 설정
            instance.tags.clear()
            for tag in tags:
                data, _ = Tag.objects.get_or_create(name=tag)
                instance.tags.add(data)
        return instance
