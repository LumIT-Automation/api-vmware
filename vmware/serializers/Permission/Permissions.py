from rest_framework import serializers


class PermissionsSerializer(serializers.Serializer):
    class PermissionsInnerSerializer(serializers.Serializer):
        class PermissionsItemsSerializer(serializers.Serializer):
            class PermissionsPermissionSerializer(serializers.Serializer):
                object_id = serializers.IntegerField(required=False)
                name = serializers.CharField(max_length=63, required=False)
                moId = serializers.CharField(max_length=63, required=False)
                asset_id = serializers.IntegerField(required=False)
                object_type = serializers.CharField(max_length=63, required=True)

            id = serializers.IntegerField(required=True)
            identity_group_name = serializers.CharField(max_length=63, required=True)
            identity_group_identifier = serializers.CharField(max_length=255, required=True)
            role = serializers.CharField(max_length=64, required=True)
            object = PermissionsPermissionSerializer(required=True)

        items = PermissionsItemsSerializer(many=True)

    data = PermissionsInnerSerializer(required=True)
