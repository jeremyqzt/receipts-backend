from django.contrib import admin
from .models import Bucket, ActiveBucket


class BucketAdmin(admin.ModelAdmin):
    list_display = ["name", "alive", "create_date", "description", "created_by"]


class ActiveBucketAdmin(admin.ModelAdmin):
    list_display = ["main_for", "bucket"]


admin.site.register(Bucket, BucketAdmin)
admin.site.register(ActiveBucket, ActiveBucketAdmin)
