from rest_framework import serializers

from book.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["tag_id", "tag_name"]
