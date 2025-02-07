from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class UserRole(models.TextChoices):
    ADMIN = 'admin'
    USER = 'user'

# Create your models here.
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    role = models.CharField(choices=UserRole.choices, default=UserRole.USER, max_length=10)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
