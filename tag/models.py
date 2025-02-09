from django.db import models

from common.models import TimeStampModel

class TagFilterOption(models.TextChoices):
    AND = "and"
    OR = "or"

class Tag(TimeStampModel):
    tag_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    objects = models.Manager()

    class Meta:
        db_table = "tag"
        indexes = [
            models.Index(fields=["name"]),
        ]
