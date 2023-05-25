import math
from django.db.models import Q
from uploader.models import ProcessedState

from uploader.utils import get_sort_text
from uploader.models import Receipt
from uploader.constants import RECEIPT_COUNT_DEFAULT
from uploader.exceptions import NoSuchReceiptForUser


class ReceiptService:
    def __init__(self, user):
        self.user = user

    def get_count(self, bucket):
        files = Receipt.objects.filter(uploaded_by=self.user, alive=True, bucket=bucket)
        return files.count()


    def get_receipts(self, bucket, sort=None, start=0, count = RECEIPT_COUNT_DEFAULT, searchTerm=None):

        start = int(start)
        count = int(count)

        files = Receipt.objects.filter(uploaded_by=self.user, alive=True, bucket=bucket)
        if searchTerm:
            files=files.filter(
                Q(description__icontains=searchTerm) |
                Q(vendor__icontains=searchTerm)
            )
        files = files.order_by(get_sort_text(sort), '-pk')
        ret_count = files.count()
        num_pages = math.ceil(ret_count/count)
        ret = files[start*count:start*count+count]

        return ret_count, num_pages, ret

    def update_receipt(self, pk, update_fields):
        instance, created = Receipt.objects.get_or_create(uploaded_by=self.user, alive=True, pk=pk)
        if not created and instance:
            for attr, value in update_fields.items(): 
                setattr(instance, attr, value)
            instance.save()
            return instance

        raise NoSuchReceiptForUser

    def update_image(self, pk, file):
        try:
            receipt_obj = Receipt.objects.get(pk=pk, alive=True, uploaded_by=self.user)
            receipt_obj.file = file
            receipt_obj.thumbnail_file = file
            receipt_obj.status = ProcessedState.NOT_REQUIRED
            receipt_obj.threshhold_file = None
            receipt_obj.parsed_file = None
            receipt_obj.cropped_file = None
            receipt_obj.save()
            return receipt_obj
        except:
            return None


