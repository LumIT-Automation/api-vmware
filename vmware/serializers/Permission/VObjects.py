from rest_framework import serializers

from vmware.serializers.Permission.VObject import PermissionVObjectSerializer


class PermissionVObjectsSerializer(serializers.Serializer):
    items = PermissionVObjectSerializer(many=True)
