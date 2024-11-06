from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    # Not using composition here, for simpler data structure exposed to consumer.

    class PermissionObjectSerializer(serializers.Serializer):
        id_asset = serializers.IntegerField(required=True)
        asset_name = serializers.CharField(max_length=256, required=False)
        moId = serializers.CharField(required=True, max_length=63)
        name = serializers.CharField(required=True, max_length=63)

    id = serializers.IntegerField(required=False)
    identity_group_name = serializers.CharField(required=False, max_length=63)
    identity_group_identifier = serializers.CharField(required=True, max_length=255)
    role = serializers.CharField(required=True, max_length=64)
    object = PermissionObjectSerializer(required=True)
