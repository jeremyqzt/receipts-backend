from django.db import models
from django.contrib.auth.models import User

class PremiumLevels(models.IntegerChoices):
    UNLIMITED_RECEIPTS = 1
    UNLIMITED_BUCKETS_RECEIPTS = 2

class Premium(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField(
        choices=PremiumLevels.choices
    )