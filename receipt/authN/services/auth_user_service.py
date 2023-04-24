from datetime import datetime

from buckets.models import ActiveBucket
from buckets.constants import DEFAULT_BUCKET
from buckets.serializers import BucketCreateSerializer
from userSettings.models import UserSettings, UserSetupState, UserAccountCreationState

def create_initial_bucket(user):
    serializer = BucketCreateSerializer(data=DEFAULT_BUCKET)

    if serializer.is_valid():
        bucket_inst = serializer.save(created_by=user)
        ActiveBucket.objects.create(main_for=user, bucket=bucket_inst)
        

def create_user_settings(user):
    UserSettings.objects.create(
        user=user,
        last_modified=datetime.now(),
        contact_email=user.username,
        text_address="",
        text_phone=""
    )


class AuthUserService():
    def __init__(self, user):
        self.user = user

    def setup_user(self):
        setup_status = UserSetupState.objects.create(user=self.user, status=UserAccountCreationState.ACCOUNT_CREATED)
        create_initial_bucket(self.user)
        setup_status.status = UserAccountCreationState.INIT_BUSINESS_CREATED
        setup_status.save()
        create_user_settings(self.user)
        setup_status.status = UserAccountCreationState.INIT_SETTINGS_CREATED
        setup_status.save()
