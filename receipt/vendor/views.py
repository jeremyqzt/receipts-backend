from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Vendor
from .serializers import VendorDeleteSerializer, VendorSerializer, VendorCreateSerializer

class VendorView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        buckets = Vendor.objects.filter(created_by=request.user, alive=True)
        ret_obj = VendorSerializer(buckets, many=True)
        return Response(ret_obj.data)

    def post(self, request):
        inst = None
        serializer = VendorCreateSerializer(data=request.data)

        if serializer.is_valid():
            inst = serializer.save(created_by=request.user)

        if inst:
            ret_obj = VendorSerializer(inst, many=False)
            return Response(ret_obj.data)

        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors}
        )

class VendorDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print(request.data)
        serializer = VendorDeleteSerializer(data=request.data, user=request.user)

        if serializer.is_valid():
            serializer.deactivate()
            return Response(request.data)

        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"error": serializer.errors}
        )