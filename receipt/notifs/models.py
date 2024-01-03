from django.db import models

class Notification(models.Model):
    message = models.TextField()
    timeStamp = models.DateTimeField(auto_now=True)
    alive = models.BooleanField()
