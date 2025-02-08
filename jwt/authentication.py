from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

import jwt
from jwt.models import Token

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):

    AUTH_HEADER = settings.AUTH_HEADER + " "

    def authenticate(self, request) -> tuple[User, dict]:
        # 헤더에서 JWT 추출
        jwt_token: str = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None or not jwt_token.startswith(self.AUTH_HEADER):
            raise AuthenticationFailed("Authentication header missing or invalid")

        # 앞에 붙은 Bearer 떼버리기
        raw_token = jwt_token.split(self.AUTH_HEADER)[1].strip()

        # Refresh Token 사용하면 안됨
        if Token.objects.filter(token=raw_token).exists():
            raise AuthenticationFailed("This is not valid access token")

        # Access 토큰이 유효한지 확인
        if Token.objects.is_valid(token=raw_token):
            payload = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
        else:
            raise AuthenticationFailed("Invalid signature")

        # 데이터베이스에서 사용자 정보 가져오기
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise AuthenticationFailed("User identifier not found in JWT")

        user = User.objects.filter(id=user_id).first()
        if user is None:
            raise AuthenticationFailed("User not found")

        # Return the user and token payload
        return user, payload

    def authenticate_header(self, request):
        return self.AUTH_HEADER
