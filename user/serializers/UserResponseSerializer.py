from rest_framework.serializers import ModelSerializer
from user.models import User

class UserResponseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']