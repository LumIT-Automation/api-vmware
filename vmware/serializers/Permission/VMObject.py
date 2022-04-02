from rest_framework import serializers


class PermissionVMObjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    id_asset = serializers.IntegerField(required=True)
    moId = serializers.CharField(required=True, max_length=63)
    name = serializers.CharField(required=True, max_length=255, allow_blank=True)
    object_type = serializers.CharField(required=False, max_length=15, allow_null=True)
    description = serializers.CharField(required=False, max_length=255, allow_blank=True)
