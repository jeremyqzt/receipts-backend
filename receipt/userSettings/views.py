from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from userSettings.service import UserSettingService
from userSettings.serializer import UserSettingsSerializer, UserSettingsUpdateSerializer

class UserSettingsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_inst = request.user

        if user_inst:
            user_service = UserSettingService(user_inst)
            user_settings = user_service.get_user_settings()

            ret_obj = UserSettingsSerializer(user_settings, many=False)
            return Response(ret_obj.data)
        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={"message": "No Such User"},
        )

    def post(self, request):
        user_inst = request.user
        data_inst = UserSettingsUpdateSerializer(request.data)

        print(data_inst)
        if user_inst and data_inst:
            user_service = UserSettingService(user_inst)
            user_settings = user_service.update_user_settings(data_inst)
            ret_obj = UserSettingsSerializer(user_settings, many=False)
            return Response(ret_obj.data)

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={"message": "No such user or missing data"},
        )
