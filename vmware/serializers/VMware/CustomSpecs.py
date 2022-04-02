from rest_framework import serializers

from vmware.serializers.VMware.CustomSpec import VMwareCustomizationSpecSerializer


class VMwareCustomizationSpecsSerializer(serializers.Serializer):
    items = VMwareCustomizationSpecSerializer(many=True)

