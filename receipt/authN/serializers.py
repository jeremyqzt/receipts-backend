from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = make_password(validated_data.pop("password"))

        user_obj = User.objects.create(
            username=username,
            email=username,
            password=password,
        )

        return user_obj


class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = make_password(validated_data.pop("password"))

        user_obj = User.objects.get(
            username=username,
            email=username,
        )

        if user_obj:
            if password:
                user_obj.password = password
            if username:
                user_obj.username = username
                user_obj.email = username

        return user_obj


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import timedelta
from .mfaViews import get_user_totp_device


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['mfaRequired'] = False

        new_token = refresh.access_token
        new_token.set_exp(lifetime=timedelta(days=7))
        device = get_user_totp_device(self, self.user)
        if device and device.confirmed:
            new_token.set_exp(lifetime=timedelta(seconds=45))
            data['mfaRequired'] = True
        data['access'] = str(new_token)

        return data