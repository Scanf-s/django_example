from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jwt_auth.authentication import JWTAuthentication
from tag.models import Tag
from tag.serializers.tag_create_serializer import TagCreateSerializer
from tag.serializers.tag_serializer import TagSerializer
from tag.serializers.tag_update_serializer import TagUpdateSerializer
from user.permissions import IsAdminUser


class TagView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request) -> Response:
        # 모든 태그 조회
        tags: Tag = Tag.objects.all()
        if not tags:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer: TagSerializer = TagSerializer(instance=tags, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        # 태그 생성
        serializer: TagCreateSerializer = TagCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class TagDetailView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        else:
            return [IsAdminUser()]

    def get(self, request, **kwargs) -> Response:
        # 태그 ID로 태그 이름 조회
        tag: Tag = Tag.objects.filter(tag_id=kwargs.get("tag_id")).first()
        if not tag:
            raise NotFound("Tag not found")

        serializer: TagSerializer = TagSerializer(instance=tag)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, **kwargs):
        # 태그 ID로 태그 이름 변경
        tag: Tag = Tag.objects.filter(tag_id=kwargs.get("tag_id")).first()
        if not tag:
            raise NotFound("Tag not found")

        serializer: TagUpdateSerializer = TagUpdateSerializer(
            instance=tag, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        # 태그 삭제
        tag: Tag = Tag.objects.filter(tag_id=kwargs.get("tag_id")).first()
        if not tag:
            raise NotFound("Tag not found")

        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
