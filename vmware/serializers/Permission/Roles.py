from rest_framework import serializers

from vmware.serializers.Permission.Role import RoleSerializer


class RolesSerializer(serializers.Serializer):
    items = RoleSerializer(many=True)
