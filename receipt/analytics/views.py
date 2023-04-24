from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from uploader.models import Receipt

from buckets.service import BucketService

from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Avg, Sum, Count

import datetime


class AnalyticsMonthlyTotalsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        request_for = request.user
        bucket = BucketService(request.user).get_active_bucket()
        this_year = datetime.datetime.now() - datetime.timedelta(days=365)

        total_by_user_by_month = Receipt.objects.filter(alive=True, uploaded_by=request_for, bucket=bucket, receipt_date_datetime__gte=this_year).annotate(month=ExtractMonth('receipt_date_datetime'),
                                                                                                                                                           year=ExtractYear('receipt_date_datetime'),).order_by().values('year', 'month').annotate(total=Sum('total_amount')).values('year', 'month', 'total')

        return Response(total_by_user_by_month)


class AnalyticsMonthlyAverageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request_for = request.user
        bucket = BucketService(request.user).get_active_bucket()
        this_year = datetime.datetime.now() - datetime.timedelta(days=365)

        avg_by_user_by_month = Receipt.objects.filter(alive=True, uploaded_by=request_for, bucket=bucket, receipt_date_datetime__gte=this_year).annotate(month=ExtractMonth('receipt_date_datetime'),
                                                                                                                                                         year=ExtractYear('receipt_date_datetime'),).order_by().values('year', 'month').annotate(average=Avg('total_amount')).values('year', 'month', 'average')

        return Response(avg_by_user_by_month)


class AnalyticsVendorFrequencyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request_for = request.user
        bucket = BucketService(request.user).get_active_bucket()
        this_year = datetime.datetime.now() - datetime.timedelta(days=365)

        vendor_total = Receipt.objects.filter(alive=True, uploaded_by=request_for, bucket=bucket, receipt_date_datetime__gte=this_year).values(
            'vendor').annotate(total=Count('vendor')).order_by('total')

        return Response(vendor_total)


class AnalyticsCategoryTotalView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request_for = request.user
        bucket = BucketService(request.user).get_active_bucket()
        this_year = datetime.datetime.now() - datetime.timedelta(days=365)

        total_by_user_by_month_bycategory = \
            Receipt.objects.filter(uploaded_by=request_for,
                                   bucket=bucket, receipt_date_datetime__gte=this_year, alive=True) \
            .annotate(month=ExtractMonth('receipt_date_datetime'),
                      year=ExtractYear('receipt_date_datetime')) \
            .order_by().values('year', 'month', 'category').annotate(total=Sum('total_amount')).values('year', 'month', 'category', 'total')

        return Response(total_by_user_by_month_bycategory)


class AnalyticsReceiptCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request_for = request.user
        bucket = BucketService(request.user).get_active_bucket()
        this_year = datetime.datetime.now() - datetime.timedelta(days=365)

        receipt_total = Receipt.objects.filter(
            alive=True, uploaded_by=request_for, bucket=bucket, receipt_date_datetime__gte=this_year).count()
        return Response(receipt_total)


class AnalyticsReceiptCategoryCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        request_for = request.user
        bucket = BucketService(request.user).get_active_bucket()
        this_year = datetime.datetime.now() - datetime.timedelta(days=365)

        category_total = Receipt.objects.filter(alive=True, uploaded_by=request_for, bucket=bucket, receipt_date_datetime__gte=this_year).values(
            'category').annotate(total=Count('category')).order_by('total')

        return Response(category_total)
