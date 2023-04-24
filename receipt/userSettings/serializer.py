from rest_framework import serializers

class UserSettingsSerializer(serializers.Serializer):
    last_modified = serializers.DateTimeField(required=False)
    contact_email = serializers.CharField(required=False)
    text_address = serializers.CharField(required=False)
    text_phone = serializers.CharField(required=False)
    can_contact = serializers.BooleanField(required=False)

class UserSettingsUpdateSerializer(serializers.Serializer):
    action = serializers.IntegerField(required=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    contact = serializers.BooleanField(required=False)



