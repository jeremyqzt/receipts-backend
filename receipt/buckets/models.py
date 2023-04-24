from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.files.storage import default_storage
import uuid
from django.conf import settings

def logo_file_name(_, filename):
    return "logos/" + str(uuid.uuid4()) + " " + filename


class Bucket(models.Model):
    alive = models.BooleanField()
    name = models.TextField()
    create_date = models.DateField(auto_now_add=True, blank=True)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    logo = models.ImageField(default=None, null=True, upload_to=logo_file_name, storage=default_storage)

    @property
    def image_url(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=86400)

        if self.logo and hasattr(self.logo, "name"):
            blob = settings.BUCKET.get_blob(self.logo.name)
            return blob.generate_signed_url(expiration=expires)

        return ""

class ActiveBucket(models.Model):
    main_for = models.ForeignKey(User, on_delete=models.CASCADE)
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
