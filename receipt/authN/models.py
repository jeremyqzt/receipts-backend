from django.db import models

class PasswordReset(models.Model):
    username = models.TextField()
    uuid = models.UUIDField()
    timeStamp = models.DateTimeField(auto_now=True)


class PasswordResetRequest(models.Model):
    username = models.TextField()
    description = models.TextField()
    accepted = models.BooleanField(default=False)
    timeStamp = models.DateTimeField(auto_now=True)