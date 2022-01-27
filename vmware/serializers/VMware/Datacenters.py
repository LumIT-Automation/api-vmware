from rest_framework import serializers

from vmware.serializers.VMware.Datacenter import VMwareDatacenterInnerSerializer


class VMwareDatacentersSerializer(serializers.Serializer):
    class VMwareDatacentersInnerSerializer(serializers.Serializer):
        items = VMwareDatacenterInnerSerializer(many=True)

    data = VMwareDatacentersInnerSerializer(required=True)
