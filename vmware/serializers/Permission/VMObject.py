from rest_framework import serializers


class PermissionVMObjectSerializer(serializers.Serializer):
    class PermissionVMObjectInnerSerializer(serializers.Serializer):
        id_asset = serializers.IntegerField(required=False)
        moId = serializers.CharField(max_length=63, required=False)
        name = serializers.CharField(max_length=255, required=False, allow_blank=True)
        description = serializers.CharField(max_length=255, required=False, allow_blank=True)

    data = PermissionVMObjectInnerSerializer(required=True)
