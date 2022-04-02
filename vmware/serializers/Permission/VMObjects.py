from rest_framework import serializers

from vmware.serializers.Permission.VMObject import PermissionVMObjectSerializer


class PermissionVMObjectsSerializer(serializers.Serializer):
    items = PermissionVMObjectSerializer(many=True)
