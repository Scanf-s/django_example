from rest_framework import serializers

from tag.models import Tag


class TagUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["name"]

    def validate_name(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("Invalid tag name")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance
