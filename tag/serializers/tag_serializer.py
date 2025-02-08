from rest_framework import serializers

from tag.models import Tag


class TagSerializer(serializers.ModelSerializer):
    tag_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ["tag_id", "name"]

    def validate_name(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("Invalid tag name")
        return value

    def create(self, validated_data):
        return Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance
