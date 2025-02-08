from rest_framework import serializers

from book.models import Book
from tag.serializers.tag_serializer import TagSerializer


class BookResponseSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    class Meta:
        model = Book
        fields = ["book_id", "isbn", "title", "author", "stock", "tags"]
