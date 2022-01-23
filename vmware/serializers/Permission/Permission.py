from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    class PermissionInnerSerializer(serializers.Serializer):
        class PermissionPermissionSerializer(serializers.Serializer):
            id_asset = serializers.IntegerField(required=True)
            moId = serializers.CharField(max_length=63, required=True)
            name = serializers.CharField(max_length=63, required=False)

        identity_group_identifier = serializers.CharField(max_length=255, required=True)
        role = serializers.CharField(max_length=64, required=True)
        object = PermissionPermissionSerializer(required=True)

    data = PermissionInnerSerializer(required=True)
