from rest_framework import serializers
from book.models import Book

class BookResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'description', 'stock', 'tags']