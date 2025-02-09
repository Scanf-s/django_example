from rest_framework import serializers

from tag.models import Tag


class TagSerializer(serializers.ModelSerializer):
    tag_id = serializers.IntegerField()
    name = serializers.CharField(required=False)

    class Meta:
        model = Tag
        fields = ["tag_id", "name"]
