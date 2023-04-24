from django.contrib import admin
from .models import PasswordReset

class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ["username", "uuid"]


admin.site.register(PasswordReset, PasswordResetAdmin)
# Register your models here.
