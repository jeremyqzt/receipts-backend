from django.contrib import admin
from .models import Receipt


class ReceiptAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Receipt._meta.get_fields()]


admin.site.register(Receipt, ReceiptAdmin)
