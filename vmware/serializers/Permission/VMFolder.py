from rest_framework import serializers


class PermissionVMFoldersSerializer(serializers.Serializer):
    class PermissionVMFoldersInnerSerializer(serializers.Serializer):
        class PermissionVMFoldersItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            id_asset = serializers.IntegerField(required=True)
            name = serializers.CharField(max_length=255, required=False, allow_blank=True)
            description = serializers.CharField(max_length=255, required=False, allow_blank=True)

        items = PermissionVMFoldersItemsSerializer(many=True)

    data = PermissionVMFoldersInnerSerializer(required=True)
