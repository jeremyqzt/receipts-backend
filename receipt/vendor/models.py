from django.db import models
from django.contrib.auth.models import User

class Vendor(models.Model):
    alive = models.BooleanField()
    name = models.TextField()
    create_date = models.DateField(auto_now_add=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

