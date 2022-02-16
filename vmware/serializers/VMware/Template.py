from rest_framework import serializers


class VMwareDeployTemplateSerializer(serializers.Serializer):
    class VMwareDeployTemplateInnerSerializer(serializers.Serializer):
        class VMwareVirtualMachineNetworkDevicesSerializer(serializers.Serializer):
            networkMoId = serializers.CharField(max_length=255, required=False)
            label = serializers.CharField(max_length=255, required=True)
            deviceType = serializers.CharField(max_length=64, required=False, allow_blank=True)

        vmName = serializers.CharField(max_length=255, required=True)
        datacenterId = serializers.CharField(max_length=64, required=True)
        clusterId = serializers.CharField(max_length=64, required=True)
        datastoreId = serializers.CharField(max_length=64, required=True)
        vmFolderId = serializers.CharField(max_length=64, required=True)
        powerOn = serializers.BooleanField(required=False)
        guestSpec = serializers.CharField(max_length=255, required=False)
        networkDevices = VMwareVirtualMachineNetworkDevicesSerializer(many=True, required=False, allow_null=True)

    data = VMwareDeployTemplateInnerSerializer(required=True)
