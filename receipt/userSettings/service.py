
from userSettings.models import UserSettings

from userSettings.constants import (
    CHANGE_PASSWORD,
    CHANGE_CONTACT_EMAIL,
    CHANGE_CONTACT_PHONE,
    CHANGE_CONTACT_ADDRESS,
    CHANGE_CONTACT_CAN_CONTACT
)
from django.contrib.auth.hashers import make_password

class UserSettingService:
    def __init__(self, user):
        self.user = user

    def get_user_settings(self):
        return UserSettings.objects.get(user=self.user)

    def update_user_settings(self, data_inst):
        user_settings = UserSettings.objects.get(user=self.user)

        if data_inst.data['action'] == CHANGE_PASSWORD:
            self.user.password = make_password(data_inst.data['password'])
            self.user.save()

        if data_inst.data['action'] == CHANGE_CONTACT_EMAIL:
            user_settings.contact_email = data_inst.data['username']
            user_settings.save()

        if data_inst.data['action'] == CHANGE_CONTACT_PHONE:
            user_settings.text_phone = data_inst.data['phone']
            user_settings.save()

        if data_inst.data['action'] == CHANGE_CONTACT_ADDRESS:
            user_settings.text_address = data_inst.data['address']
            user_settings.save()

        if data_inst.data['action'] == CHANGE_CONTACT_CAN_CONTACT:
            user_settings.can_contact = data_inst.data['contact']
            user_settings.save()

        return UserSettings.objects.get(user=self.user)