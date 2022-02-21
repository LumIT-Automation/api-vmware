from rest_framework import serializers


class VMwareDeployTemplateSerializer(serializers.Serializer):
    class VMwareVirtualMachineNetworkDeviceTypeSerializer(serializers.Serializer):
        class VMwareVirtualMachineNetworkDevicesSerializer(serializers.Serializer):
            networkMoId = serializers.CharField(max_length=255, required=False)
            label = serializers.CharField(max_length=255, required=False, allow_blank=True)
            deviceType = serializers.CharField(max_length=64, required=False, allow_blank=True)

        existent = VMwareVirtualMachineNetworkDevicesSerializer(many=True, required=False, allow_null=True)
        new = VMwareVirtualMachineNetworkDevicesSerializer(many=True, required=False, allow_null=True)

    class VMwareVirtualMachineDiskDeviceTypeSerializer(serializers.Serializer):
        class VMwareVirtualMachineDiskDevicesSerializer(serializers.Serializer):
            datastoreMoId = serializers.CharField(max_length=255, required=False)
            label = serializers.CharField(max_length=255, required=False, allow_blank=True)
            sizeMB = serializers.IntegerField(required=True)
            deviceType = serializers.CharField(max_length=64, required=False, allow_blank=True)

        existent = VMwareVirtualMachineDiskDevicesSerializer(many=True, required=False, allow_null=True)
        new = VMwareVirtualMachineDiskDevicesSerializer(many=True, required=False, allow_null=True)

    vmName = serializers.CharField(max_length=255, required=True)
    datacenterMoId = serializers.CharField(max_length=64, required=True)
    clusterMoId = serializers.CharField(max_length=64, required=True)
    datastoreMoId = serializers.CharField(max_length=64, required=True)
    vmFolderMoId = serializers.CharField(max_length=64, required=True)
    powerOn = serializers.BooleanField(required=False)
    guestSpec = serializers.CharField(max_length=255, required=False, allow_blank=True)
    networkDevices = VMwareVirtualMachineNetworkDeviceTypeSerializer(required=False, allow_null=True)
    diskDevices = VMwareVirtualMachineDiskDeviceTypeSerializer(required=False, allow_null=True)
