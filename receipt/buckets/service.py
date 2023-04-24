from .models import ActiveBucket

class BucketService:
    def __init__(self, user):
        self.user = user

    def get_active_bucket(self):
        active_bucket = ActiveBucket.objects.filter(main_for=self.user).first().bucket
        return active_bucket