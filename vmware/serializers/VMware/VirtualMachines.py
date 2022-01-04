from rest_framework import serializers


class VMwareVirtualMachinesSerializer(serializers.Serializer):
    class VMwareVirtualMachinesInnerSerializer(serializers.Serializer):
        class VMwareVirtualMachinesItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        items = VMwareVirtualMachinesItemsSerializer(many=True)

    data = VMwareVirtualMachinesInnerSerializer(required=True)
