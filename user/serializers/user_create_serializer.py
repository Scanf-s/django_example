from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from user.models import User


class UserCreateSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def validate(self, attrs):
        email = attrs.get("email")
        validate_email(email)  # exception 발생 안하면 통과

        password: str = attrs.get("password")
        validate_password(password)  # exception 발생 안하면 통과

        return attrs

    def create(self, validated_data):
        # 관리자 계정은 직접 데이터베이스에서 생성해야함
        return User.objects.create_user(**validated_data)
