from rest_framework import serializers

from tag.models import Tag


class TagCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["tag_id", "name"]

    def validate_name(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("Invalid tag name")
        return value

    def create(self, validated_data):
        return Tag.objects.create(**validated_data)
