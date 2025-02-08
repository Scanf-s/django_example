from typing import Dict

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import exception_handler
from jwt.authentication import JWTAuthentication
from jwt.manager import TokenManager
from user.manager import UserManager


@exception_handler
class LoginView(APIView):
    """
    Access token 발급받는 View (로그인)
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request) -> Response:
        email: str = request.data.get("email")
        password: str = request.data.get("password")
        data: Dict[str, str] = UserManager.login(email=email, password=password)
        return Response(data=data, status=status.HTTP_200_OK)


@exception_handler
class LogoutView(APIView):
    """
    Refresh token 폐기하는 View (로그아웃)
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request) -> Response:
        refresh_token: str = request.data.get("refresh_token")
        TokenManager().discard_refresh(user=request.user, token=refresh_token)
        return Response(status=status.HTTP_204_NO_CONTENT)
