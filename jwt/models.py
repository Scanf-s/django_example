from django.db import models

class Token(models.Model):
    token_id = models.BigAutoField(primary_key=True)
    user_id = models.OneToOneField(to="users.User", on_delete=models.CASCADE)
    token = models.CharField(max_length=255)

    class Meta:
        db_table = "token"