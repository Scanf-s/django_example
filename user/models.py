from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin"
    USER = "user"


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, null=True)
    role = models.CharField(
        choices=UserRole.choices, default=UserRole.USER, max_length=10
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"
