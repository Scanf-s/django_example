from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from jwt.models import Token

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request) -> Response:
        refresh_token = request.data.get("refresh_token")
        access_token: str = Token.objects.renew(refresh_token=refresh_token)
        return Response(data={"access_token": access_token, "refresh_token": refresh_token}, status=status.HTTP_200_OK)
