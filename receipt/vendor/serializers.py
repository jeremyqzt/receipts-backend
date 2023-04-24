from rest_framework import serializers
from .models import Vendor


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = "__all__"

class VendorCreateSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        created_by = validated_data.pop("created_by")
        name = validated_data.pop("name")
        vendor_obj = Vendor.objects.create(
            alive=True,
            created_by=created_by,
            name=name,
        )

        return vendor_obj


class VendorDeleteSerializer:
    def __init__(self, data, user):
        self.data = data
        self.user = user
        self.vendor = None
        self.errors = None

    def is_valid(self):
        uid = self.data.get("uid", None)
        try:
            self.vendor = Vendor.objects.get(
                alive=True,
                pk=uid,
                created_by=self.user,
            )
        except Vendor.DoesNotExist:
            self.errors = "Matching vendor does not exist or is already inactive"
            self.vendor = None

        return self.vendor is not None

    def deactivate(self):
        self.vendor.delete()
