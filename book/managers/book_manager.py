from typing import Dict

from django.db.models import Manager
from django.db.models.query import QuerySet


class BookManager(Manager):

    def get_all_books(self, request) -> QuerySet:
        return self.all()

    def create_book(self, request_body: Dict[str, str]) -> QuerySet:
        return self.create(**request_body)
