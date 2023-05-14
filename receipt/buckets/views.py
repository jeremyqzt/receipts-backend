from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from buckets.serializers import (
    BucketCreateSerializer,
    BucketSerializer,
    BucketDeleteSerializer,
)
from rest_framework.permissions import IsAuthenticated
from .models import Bucket, ActiveBucket


class BucketView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        buckets = Bucket.objects.filter(created_by=request.user, alive=True)
        ret_obj = BucketSerializer(buckets, many=True)
        return Response(ret_obj.data)

    def post(self, request):
        bucket_inst = None
        serializer = BucketCreateSerializer(data=request.data)

        num_buckets = Bucket.objects.filter(created_by=request.user, alive=True).count()
        if num_buckets >= 6:
            return Response(
                status=status.HTTP_402_PAYMENT_REQUIRED, data={"error": "6 Bucket limit reached"}
            )

        if serializer.is_valid():
            bucket_inst = serializer.save(created_by=request.user)

        if bucket_inst:
            ret_obj = BucketSerializer(bucket_inst, many=False)
            return Response(ret_obj.data)

        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors}
        )


class BucketDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_inst = BucketDeleteSerializer(data=request.data, user=request.user)
        if data_inst.is_valid():
            data_inst.deactivate()
            return Response(data_inst.data)

        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={"errors": data_inst.errors}
        )


class ActiveBucketView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        active_bucket = ActiveBucket.objects.filter(main_for=request.user).first()
        if active_bucket:
            ret_obj = BucketSerializer(active_bucket.bucket, many=False)
            return Response(ret_obj.data)
        return Response({})

    def post(self, request):
        bucket_inst = ActiveBucket.objects.filter(main_for=request.user).first()
        new_bucket = request.data.get("bucket")
        new_buct_inst = Bucket.objects.get(pk=new_bucket)

        if bucket_inst:
            bucket_inst.bucket = new_buct_inst
            bucket_inst.save()
        else:
            ActiveBucket.objects.create(main_for=request.user, bucket=new_buct_inst)

        return Response(BucketSerializer(new_buct_inst, many=False).data)
