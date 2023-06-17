from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uploader.serializers import UploadedItemSerializer, UploadedItemCreateSerializer, ReceiptDeleteSerializer, ReceiptReParseSerializer
from rest_framework.permissions import IsAuthenticated
from .readerMain import ReceiptProcessorThread
from uploader.constants import RECEIPT_COUNT_DEFAULT, RECEIPT_COUNT_LIMIT
from uploader.receiptService import ReceiptService
from buckets.service import BucketService


class ReceiptEditView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        service = ReceiptService(request.user)

        try:
            inst = service.update_receipt(
                request.data['uid'], request.data['update_data'])
            ret_obj = UploadedItemSerializer(inst, many=False)
            return Response(status=status.HTTP_200_OK, data=ret_obj.data)
        except:
            pass

        return Response(status=status.HTTP_400_BAD_REQUEST, data={"errors": "Something unexpected happened!"})


class ReceiptImageEditView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        service = ReceiptService(request.user)

        try:
            inst = service.update_image(
                request.data['uid'], request.data['file'])
            ret_obj = UploadedItemSerializer(inst, many=False)
            return Response(status=status.HTTP_200_OK, data=ret_obj.data)
        except:
            pass

        return Response(status=status.HTTP_400_BAD_REQUEST, data={"errors": "Something unexpected happened!"})


class ReceiptView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        searchTerm = request.GET.get('searchTerm', None)
        sort = request.GET.get('searchParam', None)
        start = request.GET.get('offset', 0)
        limit = request.GET.get("limit", RECEIPT_COUNT_DEFAULT)

        service = ReceiptService(request.user)
        bucket = BucketService(request.user).get_active_bucket()

        ret_count, num_pages, files = service.get_receipts(
            bucket, sort, start, limit, searchTerm)

        ret_obj = UploadedItemSerializer(files, many=True)

        return_data = {
            "receipts": ret_obj.data,
            "pages": num_pages,
            "total": ret_count
        }

        return Response(return_data)

    def post(self, request):
        receipt_inst = None
        serializer = UploadedItemCreateSerializer(data=request.data)

        if serializer.is_valid():
            service = ReceiptService(request.user)
            bucket = BucketService(request.user).get_active_bucket()
            if service.get_count(bucket=bucket) <= RECEIPT_COUNT_LIMIT:
                receipt_inst = serializer.save(uploaded_by=request.user)
            else:
                return Response(status=status.HTTP_402_PAYMENT_REQUIRED, data={"errors": str(RECEIPT_COUNT_LIMIT) + " Limit Reached"})

        if receipt_inst:
            ret_obj = UploadedItemSerializer(receipt_inst, many=False)
            try:
                ReceiptProcessorThread(
                    receipt_inst.file, receipt_inst.pk).start()
            except Exception:
                return Response(status=status.HTTP_201_CREATED, data={"message": "Receipt Uploaded, but having trouble processing."})
            return Response(status=status.HTTP_200_OK, data={"message": "Processing Started.", "receipt": ret_obj.data})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={"errors": serializer.errors})


class ReceiptReParseView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_inst = ReceiptReParseSerializer(
            data=request.data, user=request.user)
        if data_inst.is_valid():
            data_inst.parse()
            return Response(data_inst.data)

        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={
                "errors": data_inst.errors}
        )


class ReceiptDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data_inst = ReceiptDeleteSerializer(
            data=request.data, user=request.user)
        if data_inst.is_valid():
            data_inst.deactivate()
            return Response(data_inst.data)

        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={
                "errors": data_inst.errors}
        )
