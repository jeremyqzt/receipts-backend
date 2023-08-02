from django.db import models

class PasswordReset(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['username', 'uuid'], name='reset_idx'),
        ]
    username = models.TextField()
    uuid = models.UUIDField()
    timeStamp = models.DateTimeField(auto_now=True)


class PasswordResetRequest(models.Model):
    username = models.TextField()
    description = models.TextField()
    accepted = models.BooleanField(default=False)
    timeStamp = models.DateTimeField(auto_now=True)