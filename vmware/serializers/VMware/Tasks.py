from rest_framework import serializers

from vmware.serializers.VMware.Task import VMwareTaskSerializer


class VMwareTasksSerializer(serializers.Serializer):
    items = VMwareTaskSerializer(many=True)
