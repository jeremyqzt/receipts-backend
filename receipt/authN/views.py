from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authN.serializers import (
    UserCreateSerializer,
    UserUpdateSerializer,
)
from rest_framework.permissions import IsAuthenticated
from authN.models import PasswordReset, PasswordResetRequest
from authN.services.auth_user_service import AuthUserService
import uuid
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist


class UserCreateView(APIView):
    def post(self, request):
        user_inst = None
        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user_inst = serializer.save()
            except Exception as e:
                return Response(
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                    data={"message": str(e)},
                )

        if user_inst:
            user_service = AuthUserService(user=user_inst)
            user_service.setup_user()
            return Response(status=status.HTTP_201_CREATED, data={"message": "created"})

        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={
                "error": serializer.errors}
        )


class UserUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_inst = None
        serializer = UserUpdateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user_inst = serializer.save()
            except Exception as e:
                return Response(
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                    data={"message": str(e)},
                )

        if user_inst:
            return Response(status=status.HTTP_200_OK, data={"message": "completed"})


class UserDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_inst = request.user
        try:
            user_inst.delete()
            return Response(status=status.HTTP_200_OK, data={"message": "completed"})
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"message": "WTF?"})


class UserForgotPasswordAdminView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_inst = request.user
        username = request.data['username']

        if user_inst.user.is_staff:
            PasswordReset.objects.create(
                username=username, uuid=str(uuid.uuid4()))
            return Response(status=status.HTTP_200_OK, data={})
        return Response(status=status.HTTP_401_UNAUTHORIZED, data={})


class UserForgotPasswordView(APIView):
    def post(self, request):
        username = request.data['username']

        try:
            PasswordReset.objects.get(username=username)
        except:
            PasswordReset.objects.create(
                username=username, uuid=str(uuid.uuid4()))
        return Response(status=status.HTTP_200_OK, data={})


class UserForgotPasswordResetView(APIView):

    def post(self, request):
        username = request.data['username']
        token = request.data['token']
        new_password = request.data['newPassword']

        reset_obj = PasswordReset.objects.get(
            username=username, uuid=token)

        if reset_obj:
            reset_obj.delete()
            user_inst = User.objects.get(
                username=username,
                email=username,
            )
            user_inst.password = make_password(new_password)
            user_inst.save()

        return Response(status=status.HTTP_200_OK, data={})


class UserForgotPasswordResetFormView(APIView):

    def post(self, request):
        username = request.data['username']
        description = request.data['description']

        try:
            reset_obj = PasswordResetRequest.objects.get(
                username=username)

            if reset_obj:
                return Response(status=status.HTTP_202_ACCEPTED, data={})
        except ObjectDoesNotExist:
            PasswordResetRequest.objects.create(username=username, description=description)

            return Response(status=status.HTTP_200_OK, data={})
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={})

