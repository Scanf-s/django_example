from django.db import models
from common.models import TimeStampModel
from jwt.manager import RefreshTokenManager


class RefreshToken(TimeStampModel):
    token_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to="user.User", on_delete=models.CASCADE)

    token = models.CharField(max_length=255)
    expired = models.BooleanField(default=False)

    objects = RefreshTokenManager()

    class Meta:
        db_table = "refresh_token"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user"]),
        ]
