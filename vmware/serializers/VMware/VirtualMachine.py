from rest_framework import serializers


class VMwareVirtualMachineSerializer(serializers.Serializer):
    class VMwareVirtualMachineNetworkDeviceTypeSerializer(serializers.Serializer):
        class VMwareVirtualMachineNetworkDevicesSerializer(serializers.Serializer):
            networkMoId = serializers.CharField(max_length=255, required=False)
            label = serializers.CharField(max_length=255, required=False, allow_blank=True)
            deviceType = serializers.CharField(max_length=64, required=False, allow_blank=True)

        existent = VMwareVirtualMachineNetworkDevicesSerializer(many=True, required=False, allow_null=True)

    class VMwareVirtualMachineDiskDeviceTypeSerializer(serializers.Serializer):
        class VMwareVirtualMachineDiskDevicesSerializer(serializers.Serializer):
            datastoreMoId = serializers.CharField(max_length=255, required=False)
            label = serializers.CharField(max_length=255, required=False, allow_blank=True)
            sizeMB = serializers.IntegerField(required=False)
            deviceType = serializers.CharField(max_length=64, required=False, allow_blank=True)

        existent = VMwareVirtualMachineDiskDevicesSerializer(many=True, required=False, allow_null=True)

    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(required=True, max_length=255)
    name = serializers.CharField(required=True, max_length=255)
    defaultDatastoreMoId = serializers.CharField(required=False, max_length=255)
    guestName = serializers.CharField(required=False, max_length=255)
    version = serializers.CharField(required=False, max_length=63)
    uuid = serializers.CharField(required=False, max_length=255)
    numCpu = serializers.IntegerField(required=False, allow_null=True)
    numCoresPerSocket = serializers.IntegerField(required=False)
    memoryMB = serializers.IntegerField(required=False)
    template = serializers.BooleanField(required=False)
    notes = serializers.CharField(max_length=2048, required=False, allow_blank=True, allow_null=True)

    networkDevices = VMwareVirtualMachineNetworkDeviceTypeSerializer(required=False, allow_null=True)
    diskDevices = VMwareVirtualMachineDiskDeviceTypeSerializer(required=False, allow_null=True)



class VMwareVirtualMachineModifySerializer(serializers.Serializer):
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

    numCpu = serializers.IntegerField(required=False)
    numCoresPerSocket = serializers.IntegerField(required=False)
    memoryMB = serializers.IntegerField(required=False)
    notes = serializers.CharField(max_length=2048, required=False, allow_blank=True, allow_null=True)
    networkDevices = VMwareVirtualMachineNetworkDeviceTypeSerializer(required=False, allow_null=True)
    diskDevices = VMwareVirtualMachineDiskDeviceTypeSerializer(required=False, allow_null=True)
