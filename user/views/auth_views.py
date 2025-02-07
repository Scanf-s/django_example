from rest_framework.views import APIView
from common.exceptions import exception_handler

@exception_handler
class LoginView(APIView):
    pass

@exception_handler
class LogoutView(APIView):
    pass