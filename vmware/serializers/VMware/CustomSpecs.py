from rest_framework import serializers

from vmware.serializers.VMware.CustomSpec import VMwareCustomizationSpecSerializer


class VMwareCustomizationSpecsSerializer(serializers.Serializer):
    items = VMwareCustomizationSpecSerializer(many=True)



class VMwareCustomizationSpecCloneSerializer(serializers.Serializer):
    class VMwareCustomizationSpecCloneInnerSerializer(serializers.Serializer):
        sourceSpec = serializers.CharField(max_length=64, required=True)
        newSpec = serializers.CharField(max_length=255, required=False)

    data = VMwareCustomizationSpecCloneInnerSerializer(required=True)
