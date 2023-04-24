from django.db import models
import datetime
from django.contrib.auth.models import User
from buckets.models import Bucket
from django.core.files.storage import default_storage
from django.conf import settings
import uuid
from cached_property import cached_property_with_ttl


class ProcessedState(models.IntegerChoices):
    UPLOADED = 1
    STARTED = 2
    CROPPED = 3
    THRESHOLD_DONE = 4
    PARSING_DONE = 5
    READING_DONE = 6
    POPULATED = 7
    UNABLE_TO_READ = 8


class ExpenseCategory(models.IntegerChoices):
    UNCATEGORIZED = 1
    PREPAY = 2
    ADVERTISING = 3
    TAX_FEE_DUE = 4
    INSURANCE = 5
    INTEREST = 6
    MAINT = 7
    MEALS = 8
    OFFICE = 9
    SALARY = 10
    STARTUP = 11
    CAR = 12


def content_file_name(_, filename):
    return "images/" + str(uuid.uuid4()) + " " + filename


class Receipt(models.Model):
    alive = models.BooleanField(default=True)
    file = models.ImageField(
        default=None, upload_to=content_file_name, storage=default_storage)
    thumbnail_file = models.ImageField(
        default=None, upload_to="thumbnail/", null=True, storage=default_storage)
    threshhold_file = models.ImageField(
        default=None, upload_to="threshhold_file/", null=True, storage=default_storage)
    parsed_file = models.ImageField(
        default=None, upload_to="parsed_image/", null=True, storage=default_storage)
    cropped_file = models.ImageField(
        default=None, upload_to="cropped_image/", null=True, storage=default_storage)
    status = models.IntegerField(
        choices=ProcessedState.choices, default=ProcessedState.UPLOADED
    )
    upload_date = models.DateField(auto_now_add=True, blank=True)
    create_date = models.DateField(auto_now_add=True, blank=True)
    receipt_date_datetime = models.DateField(
        blank=True, default=datetime.date.today)
    receipt_date = models.TextField()
    description = models.TextField()
    total_amount = models.FloatField(default=0, null=True)
    sub_amount = models.FloatField(default=0, null=True)
    all_lines = models.TextField(default="", null=True)
    vendor = models.TextField(default="", null=True, db_index=True)
    name = models.TextField()
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.IntegerField(
        choices=ExpenseCategory.choices, default=ExpenseCategory.UNCATEGORIZED
    )

    set_fields = models.JSONField("SetFields", default=dict)
    crop = models.JSONField("crop", default=dict)

    @cached_property_with_ttl(ttl=6000)
    def thumbnail(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=604800)

        if self.thumbnail_file and hasattr(self.thumbnail_file, "name"):
            blob = settings.BUCKET.get_blob(self.thumbnail_file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        return ""

    @cached_property_with_ttl(ttl=6000)
    def image_url(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=604800)

        if self.cropped_file and hasattr(self.cropped_file, "name"):
            blob = settings.BUCKET.get_blob(self.cropped_file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        if self.file and hasattr(self.file, "name"):
            blob = settings.BUCKET.get_blob(self.file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        return ""

    @cached_property_with_ttl(ttl=6000)
    def base_image_url(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=604800)

        if self.file and hasattr(self.file, "name"):
            blob = settings.BUCKET.get_blob(self.file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        return ""

    @cached_property_with_ttl(ttl=6000)
    def cropped_image_url(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=604800)
        if self.cropped_file and hasattr(self.cropped_file, "name"):
            blob = settings.BUCKET.get_blob(self.cropped_file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        return ""

    @cached_property_with_ttl(ttl=6000)
    def threshhold_file_url(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=604800)
        if self.threshhold_file and hasattr(self.threshhold_file, "name"):
            blob = settings.BUCKET.get_blob(self.threshhold_file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        return ""

    @cached_property_with_ttl(ttl=6000)
    def parsed_file_url(self):
        expires = datetime.datetime.now() + datetime.timedelta(seconds=604800)
        if self.parsed_file and hasattr(self.parsed_file, "name"):
            blob = settings.BUCKET.get_blob(self.parsed_file.name)
            return blob.generate_signed_url(version="v4", expiration=expires)

        return ""
