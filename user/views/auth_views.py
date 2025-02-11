import logging
from typing import Dict

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import custom_exception_handler
from jwt_auth.authentication import JWTAuthentication
from jwt_auth.models import Token
from user.models import User

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Access token 발급받는 View (로그인)
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @custom_exception_handler
    def post(self, request) -> Response:
        email: str = request.data.get("email")
        password: str = request.data.get("password")
        data: Dict[str, str] = User.objects.login(email=email, password=password)
        return Response(data=data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Refresh token 폐기하는 View (로그아웃)
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @custom_exception_handler
    def post(self, request) -> Response:
        refresh_token: str = request.data.get("refresh_token")
        Token.objects.discard_refresh(user=request.user, token=refresh_token)
        return Response(status=status.HTTP_204_NO_CONTENT)
