from logging.config import valid_ident
from rest_framework import serializers
from .models import Receipt
from buckets.models import Bucket
from .readerMain import ReceiptProcessorThread
from uploader.receiptService import ReceiptService
from datetime import date


class UploadedItemCreateSerializer(serializers.Serializer):
    file = serializers.FileField(default=None)
    description = serializers.CharField(default="")
    vendor = serializers.CharField(default="")
    subTotal = serializers.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, default=0)
    setFields = serializers.CharField(default="")
    crop = serializers.CharField(default="")
    bucket = serializers.IntegerField()
    category = serializers.IntegerField()

    def create(self, validated_data):
        uploaded_by = validated_data.pop("uploaded_by")
        description = validated_data.pop("description")
        crop = validated_data.pop("crop")
        vendor = validated_data.pop("vendor")
        setFields = validated_data.pop("setFields")
        subTotal = validated_data.pop("subTotal")
        total = validated_data.pop("total")
        category = validated_data.pop("category")

        file = validated_data.pop("file")
        bucket_id = validated_data.pop("bucket")

        bucket = Bucket.objects.get(pk=bucket_id)
        today = date.today()

        receipt_obj = Receipt.objects.create(
            file=file,
            uploaded_by=uploaded_by,
            description=description,
            name=file._name if file else "Quick Entry",
            bucket=bucket,
            total_amount=total,
            crop=crop,
            vendor=vendor,
            set_fields=setFields,
            sub_amount=subTotal,
            category=category,
            receipt_date=today.strftime("%Y-%m-%d")
        )

        return receipt_obj


class UploadedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = [
            "pk",
            "alive",
            "upload_date",
            "receipt_date",
            "name",
            "description",
            "uploaded_by",
            "bucket",
            "thumbnail",
            "image_url",
            "description",
            "total_amount",
            "vendor",
            "all_lines",
            "sub_amount",
            "all_lines",
            "category",
            "set_fields",
        ]


class ReceiptUpdateSerializer(serializers.Serializer):
    valid_fields = ["description", "vendor",
                    "total_amount", "sub_amount", "category"]

    def __init__(self, user):
        self.user = user

    def validate(self, data):
        validated_data = data.copy
        for key in validated_data:
            if not key in self.alid_fields:
                del validated_data[key]

        self.validated_data = validated_data

        return True

    def save(self, pk):
        if not self.validated_data:
            return

        service = ReceiptService(self.user)
        print(self.validated_data)
        return service.update_receipt(pk, self.validated_data)


class ReceiptDeleteSerializer:
    def __init__(self, data, user):
        self.data = data
        self.user = user
        self.receipt_obj = None
        self.errors = None

    def is_valid(self):
        uid = self.data.get("uid", None)
        try:
            self.receipt_obj = Receipt.objects.get(
                alive=True,
                pk=uid,
                uploaded_by=self.user,
            )
        except Receipt.DoesNotExist:
            self.errors = "Matching receipt does not exist or is already inactive"
            self.receipt_obj = None

        return self.receipt_obj is not None

    def deactivate(self):
        self.receipt_obj.alive = False
        self.receipt_obj.save()
        return UploadedItemSerializer(self.receipt_obj, many=False)


class ReceiptReParseSerializer:
    def __init__(self, data, user):
        self.data = data
        self.user = user
        self.receipt_obj = None
        self.errors = None

    def is_valid(self):
        uid = self.data.get("uid", None)
        try:
            self.receipt_obj = Receipt.objects.get(
                alive=True,
                pk=uid,
                uploaded_by=self.user,
            )
        except Receipt.DoesNotExist:
            self.errors = "Matching receipt does not exist or is already inactive"
            self.receipt_obj = None

        return self.receipt_obj is not None

    def parse(self):
        ReceiptProcessorThread(self.receipt_obj.file.path,
                               self.receipt_obj.pk).start()
