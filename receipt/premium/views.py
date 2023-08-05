from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uploader.serializers import UploadedItemSerializer, UploadedItemCreateSerializer, ReceiptDeleteSerializer, ReceiptReParseSerializer
from rest_framework.permissions import IsAuthenticated
from uploader.constants import RECEIPT_COUNT_DEFAULT, RECEIPT_COUNT_LIMIT
from uploader.receiptService import ReceiptService
from buckets.service import BucketService

# Create your views here.
class PremiumSubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response(request.data)