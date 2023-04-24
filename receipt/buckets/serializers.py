from rest_framework import serializers
from .models import Bucket, ActiveBucket
from datetime import date

COUNT_MAX = 100


class BucketCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(
        required=False, default="No Description Provided..."
    )
    create_date = serializers.DateField(required=False, default=date.today())
    file = serializers.FileField(required=False, default=None)

    def create(self, validated_data):
        created_by = validated_data.pop("created_by")
        create_date = validated_data.pop("create_date")
        description = validated_data.pop("description")
        name = validated_data.pop("name")
        file = validated_data.pop("file")

        bucket_obj = Bucket.objects.create(
            alive=True,
            created_by=created_by,
            description=description,
            name=name,
            create_date=create_date,
            logo=file,
        )

        return bucket_obj


class BucketSerializer(serializers.ModelSerializer):
    uid = serializers.IntegerField(source="pk")
    image_url =  serializers.SerializerMethodField()

    class Meta:
        model = Bucket
        fields = "__all__"

    def get_image_url(self, obj):
        return obj.image_url

class ActiveBucketSerializer(serializers.ModelSerializer):
    main_for = serializers.IntegerField(source="fk")
    bucket = serializers.IntegerField(source="fk")

    class Meta:
        model = ActiveBucket
        fields = ["bucket", "main_for"]


class BucketDeleteSerializer:
    def __init__(self, data, user):
        self.data = data
        self.user = user
        self.bucket_obj = None
        self.errors = None

    def is_valid(self):
        uid = self.data.get("uid", None)
        try:
            self.bucket_obj = Bucket.objects.get(
                alive=True,
                pk=uid,
                created_by=self.user,
            )
        except Bucket.DoesNotExist:
            self.errors = "Matching bucket does not exist or is already inactive"
            self.bucket_obj = None

        return self.bucket_obj is not None

    def deactivate(self):
        self.bucket_obj.alive = False
        self.bucket_obj.save()
        return BucketSerializer(self.bucket_obj, many=False)
