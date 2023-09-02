"""receipt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from rest_framework_simplejwt import views as jwt_views

from uploader.views import ReceiptView, ReceiptDeleteView, ReceiptReParseView, ReceiptEditView, ReceiptImageEditView
from buckets.views import BucketView, BucketDeleteView, ActiveBucketView
from authN.views import UserCreateView, UserDeleteView, UserForgotPasswordResetView, UserForgotPasswordView, UserForgotPasswordResetFormView
from authN.mfaViews import TOTPCreateView, TOTPVerifyView
from userSettings.views import UserSettingsView
from analytics.views import AnalyticsMonthlyTotalsView, AnalyticsCategoryTotalView, AnalyticsMonthlyAverageView, AnalyticsReceiptCountView, AnalyticsVendorFrequencyView, AnalyticsReceiptCategoryCountView
from vendor.views import VendorView, VendorDeleteView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

@api_view(('GET',))
def liviliness_check(_):
    return Response(status=status.HTTP_200_OK)

urlpatterns = [
    path("", liviliness_check, name="liveliness"),
    path("admin/", admin.site.urls),
    path("user/create/", UserCreateView.as_view(), name="create_user_view"),
    path("user/delete/", UserDeleteView.as_view(), name="delete_user_view"),
    path("user/forgotPassword/", UserForgotPasswordResetView.as_view(), name="forgot_password_view"),
    path("user/resetPassword/", UserForgotPasswordView.as_view(), name="reset_password_view"),
    path("user/resetPasswordForm/", UserForgotPasswordResetFormView.as_view(), name="reset_password_form_view"),
    path("user/mfaCreate/", TOTPCreateView.as_view(), name="mfaCreate"),
    path("user/mfaVerify/", TOTPVerifyView.as_view(), name="mfaVerify"),

    path(
        "auth/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/verify", jwt_views.TokenVerifyView.as_view(), name="token_verify"
    ),
    path(
        "auth/token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("api/receipt/", ReceiptView.as_view(), name="receipt"),
    path("api/receipt/delete/", ReceiptDeleteView.as_view(), name="receipt_delete"),
    path("api/receipt/update/", ReceiptEditView.as_view(), name="receipt_update"),
    path("api/receipt/updateImage/", ReceiptImageEditView.as_view(), name="receipt_image_update"),
    path("api/receipt/reprocess/", ReceiptReParseView.as_view(),
         name="receipt_reprocess"),
    path("api/bucket/", BucketView.as_view(), name="bucket"),
    path("api/vendor/", VendorView.as_view(), name="vendor"),
    path('api/vendor/delete/', VendorDeleteView.as_view(), name="vendor_delete"),
    path("api/bucket/delete/", BucketDeleteView.as_view(), name="bucket_delete"),
    path("api/active/", ActiveBucketView.as_view(), name="active_bucket"),
    path("api/settings/", UserSettingsView.as_view(), name="user_settings"),
    path("api/charts/total_costs/",
         AnalyticsMonthlyTotalsView.as_view(), name="total_costs"),
    path("api/charts/average_costs/",
         AnalyticsMonthlyAverageView.as_view(), name="average_costs"),
    path("api/charts/vendor_count/",
         AnalyticsVendorFrequencyView.as_view(), name="vendor_count"),
    path("api/charts/receipt_count/",
         AnalyticsReceiptCountView.as_view(), name="receipt_count"),
    path("api/charts/receipt_category_totals/",
         AnalyticsCategoryTotalView.as_view(), name="receipt_category_total"),
    path("api/charts/receipt_category_count/",
         AnalyticsReceiptCategoryCountView.as_view(), name="receipt_category"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
