from typing import TYPE_CHECKING, Dict

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from common.exceptions import custom_exception_handler
from jwt_auth.manager import TokenManager

if TYPE_CHECKING:
    from user.models import User


class UserManager(models.Manager):

    @custom_exception_handler
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    @custom_exception_handler
    def login(self, email, password) -> Dict[str, str]:
        user: "User" = self.filter(email=email).first()
        if not user:
            raise ObjectDoesNotExist("There is no user with this email")

        if not user.check_password(password):
            raise ValidationError("Wrong password")

        user.last_login = timezone.now()
        user.save()

        # access, refresh 토큰 생성
        token_manager: TokenManager = TokenManager()
        access_token: str = token_manager.create_token(
            user=user, token_type=token_manager.TOKEN_TYPES[0]
        )
        refresh_token: str = token_manager.create_token(
            user=user, token_type=token_manager.TOKEN_TYPES[1]
        )

        return {"access_token": access_token, "refresh_token": refresh_token}
