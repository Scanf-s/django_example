from typing import Dict

from django.db.models.query import QuerySet
from common.exceptions import exception_handler
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from user.permissions import IsAdminUser
from user.models import User, UserRole
from user.serializers.user_create_serializer import UserCreateSerializer
from user.serializers.user_response_serializer import UserResponseSerializer
from jwt.authentication import JWTAuthentication


@exception_handler
class UserView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminUser()]
        else:
            return [AllowAny()]

    def get_authenticators(self):
        if self.request.method == 'GET':
            return [JWTAuthentication()]
        else:
            return []

    def get(self, request): # 사용자 리스트
        user_queryset: QuerySet = User.objects.all()
        serializer: UserResponseSerializer = UserResponseSerializer(instance=user_queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request): # 사용자 생성 (Register)
        # Admin 계정은 데이터베이스에 직접 생성해주세요
        user_data: Dict[str, str] = request.data
        serializer: UserCreateSerializer = UserCreateSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


@exception_handler
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @classmethod
    def get_user_data(cls, user_id: str) -> Dict[str, str]:
        user: User = User.objects.filter(id=user_id).first()
        if not user:
            raise ValidationError("User not found")

        serializer: UserResponseSerializer = UserResponseSerializer(instance=user)
        return serializer.data

    def get(self, request, **kwargs) -> Response:
        user_id: str = kwargs.get("user_id")
        if not user_id:
            raise ValueError("user_id is required")

        if request.user.role == UserRole.ADMIN: # ADMIN 사용자의 경우에는, 원하는 사용자 정보를 확인할 수 있음
            data: Dict[str, str] = self.get_user_data(user_id=user_id)
            return Response(data=data, status=status.HTTP_200_OK)

        else: # 일반 사용자의 경우에는 본인것만 가능 -> 토큰에 있는 user_id 꺼내서 확인
            if request.user.id != user_id:
                raise PermissionDenied("Unauthorized access")

            data: Dict[str, str] = self.get_user_data(user_id=user_id)
            return Response(data=data, status=status.HTTP_200_OK)
