from django.utils import timezone
from django.db import models
import jwt
from django.conf import settings
from typing import TYPE_CHECKING, Optional
from user.models import User

if TYPE_CHECKING:
    from jwt.models import RefreshToken

class RefreshTokenManager(models.Manager):

    TOKEN_TYPES = ["ACCESS", "REFRESH"]

    def create_token(self, user: User, token_type: str) -> str:
        """
        토큰 생성 함수
        """
        if token_type not in self.TOKEN_TYPES:
            raise ValueError("Invalid token type provided")

        current_time = timezone.now()
        expire_time: timezone = timezone.now()

        if token_type == self.TOKEN_TYPES[0]:
            expire_time += settings.ACCESS_TOKEN_EXPIRE_TIME
        elif token_type == self.TOKEN_TYPES[1]:
            expire_time += settings.REFRESH_TOKEN_EXPIRE_TIME

        payload = {
            "user_id": user.id,
            "iat": current_time,
            "exp": expire_time
        }

        token: str = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        if token_type == self.TOKEN_TYPES[1]: # Refresh 토큰만 저장
            self.update_or_create(user=user, defaults={"token": token, "expired": False})
        return token

    def is_valid(self, token: str) -> bool:
        """
        토큰 유효성 검사 함수
        """
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return True
        except jwt.exceptions.ExpiredSignatureError:
            token_obj: Optional[RefreshToken] = self.filter(token=token).first()
            if token_obj:
                token_obj.expired = True
                token_obj.save()
            return False
        except jwt.exceptions.InvalidTokenError:
            return False

    def discard_refresh(self, token: str) -> None:
        """
        Refresh 토큰 폐기하는 함수
        """
        jwt_token: RefreshToken = self.filter(token=token).first()
        if jwt_token:
            jwt_token.delete()
        else:
            raise jwt.exceptions.InvalidTokenError("Invalid token provided when discarding token")

    def renew(self, refresh_token: str) -> str:
        """
        Access 토큰 갱신해주는 함수
        """
        if not refresh_token:
            raise jwt.exceptions.InvalidTokenError("No token provided when renewing token")

        if not self.filter(token=refresh_token).exists():
            raise jwt.exceptions.InvalidTokenError("This is not a valid refresh token")

        if self.is_valid(token=refresh_token):
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("user_id")

            user: User = User.objects.filter(id=user_id).first()
            if not user:
                raise jwt.exceptions.InvalidTokenError("Cannot find user when renewing token")
            return self.create_token(user=user, token_type=self.TOKEN_TYPES[0])
        else:
            raise jwt.exceptions.InvalidTokenError("Invalid token provided when renewing token")
