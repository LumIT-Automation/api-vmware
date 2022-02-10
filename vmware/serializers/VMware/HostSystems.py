from rest_framework import serializers

from vmware.serializers.VMware.HostSystem import VMwareHostSystemSerializer


class VMwareHostSystemsSerializer(serializers.Serializer):
    items = VMwareHostSystemSerializer(many=True)
