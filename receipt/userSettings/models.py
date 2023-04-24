from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField()
    contact_email = models.TextField()
    text_address = models.TextField()
    text_phone = models.TextField()
    can_contact = models.BooleanField(default=False)

class UserAccountCreationState(models.IntegerChoices):
    LOL_WTF_HAPPENED = 1
    ACCOUNT_CREATED = 2
    INIT_BUSINESS_CREATED = 3
    INIT_SETTINGS_CREATED = 4
    USER_CREATION_DONE = 99


class UserSetupState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=UserAccountCreationState.choices, default=UserAccountCreationState.LOL_WTF_HAPPENED
    )
