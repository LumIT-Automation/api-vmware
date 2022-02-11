from rest_framework import serializers

from vmware.serializers.VMware.Datacenter import VMwareDatacenterSerializer


class VMwareDatacentersSerializer(serializers.Serializer):
    items = VMwareDatacenterSerializer(many=True)
