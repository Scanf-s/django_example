from typing import TYPE_CHECKING, Dict
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound

from jwt_auth.models import Token

if TYPE_CHECKING:
    from user.models import User

import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def login(self, email, password) -> Dict[str, str]:
        user: "User" = self.filter(email=email).first()
        if not user:
            raise NotFound("There is no user with this email")

        if not user.check_password(raw_password=password):
            logger.debug("Wrong password")
            raise ValidationError("Wrong password")

        user.last_login = timezone.now()
        user.save()

        # access, refresh 토큰 생성
        access_token: str = Token.objects.create_token(
            user=user, token_type=Token.objects.TOKEN_TYPES[0]
        )
        refresh_token: str = Token.objects.create_token(
            user=user, token_type=Token.objects.TOKEN_TYPES[1]
        )
        return {"access_token": access_token, "refresh_token": refresh_token}
