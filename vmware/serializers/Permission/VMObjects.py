from rest_framework import serializers


class PermissionVMObjectsSerializer(serializers.Serializer):
    class PermissionVMObjectsInnerSerializer(serializers.Serializer):
        class PermissionVMObjectsItemsSerializer(serializers.Serializer):
            id = serializers.IntegerField(required=True)
            id_asset = serializers.IntegerField(required=True)
            moId = serializers.CharField(max_length=63, required=True)
            name = serializers.CharField(max_length=255, required=False, allow_blank=True)
            object_type = serializers.CharField(max_length=15, required=False, allow_null=True)
            description = serializers.CharField(max_length=255, required=False, allow_blank=True)

        items = PermissionVMObjectsItemsSerializer(many=True)

    data = PermissionVMObjectsInnerSerializer(required=True)
