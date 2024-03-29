from rest_framework import views, permissions
from rest_framework.response import Response
from rest_framework import status
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice


def get_user_totp_device(self, user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device


class TOTPCreateView(views.APIView):
    """
    Use this endpoint to set up a new TOTP device
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        device = get_user_totp_device(self, user)

        if device:
            return Response(device.confirmed, status=status.HTTP_200_OK)

        return Response(False, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        device = get_user_totp_device(self, user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False)
        url = device.config_url
        return Response(url, status=status.HTTP_201_CREATED)


class TOTPVerifyView(views.APIView):
    """
    Use this endpoint to verify/enable a TOTP device
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data["token"]
        device = get_user_totp_device(self, user)
        if not device == None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            return Response(True, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'mfaVerified': True,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class TOTPReissueView(views.APIView):
    """
    Use this endpoint to verify a TOTP, and re-issue a token
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data["token"]
        device = get_user_totp_device(self, user)
        if not device == None and device.verify_token(token):
            return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TOTDisableView(views.APIView):
    """
    Use this endpoint to verify a TOTP, and re-issue a token
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data["token"]

        device = get_user_totp_device(self, user)
        if not device == None:
            if not device == None and device.verify_token(token):
                device.confirmed = False
                device.save()
            return Response({}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)