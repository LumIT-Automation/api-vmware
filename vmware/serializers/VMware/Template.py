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

    class VMwareVirtualMachinePostDeployCommand(serializers.Serializer):
        command = serializers.CharField(required=True, max_length=64, allow_blank=True)
        user_args = serializers.JSONField(required=False)

    vmName = serializers.CharField(max_length=255, required=True)
    datacenterMoId = serializers.CharField(max_length=64, required=True)
    clusterMoId = serializers.CharField(max_length=64, required=False, allow_blank=True)
    hostMoId = serializers.CharField(max_length=64, required=False, allow_blank=True)
    vmFolderMoId = serializers.CharField(max_length=64, required=True)
    mainDatastoreMoId = serializers.CharField(max_length=64, required=True)
    powerOn = serializers.BooleanField(required=False)
    numCpu = serializers.IntegerField(required=False)
    numCoresPerSocket = serializers.IntegerField(required=False)
    memoryMB = serializers.IntegerField(required=False)
    notes = serializers.CharField(max_length=2048, required=False, allow_blank=True, allow_null=True)
    guestSpec = serializers.CharField(max_length=255, required=False, allow_blank=True)
    deleteGuestSpecAfterDeploy = serializers.BooleanField(required=False)
    secondStageIp = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
    networkDevices = VMwareVirtualMachineNetworkDeviceTypeSerializer(required=False, allow_null=True)
    diskDevices = VMwareVirtualMachineDiskDeviceTypeSerializer(required=False, allow_null=True)
    bootstrapKeyId = serializers.IntegerField(required=False)

    postDeployCommands = VMwareVirtualMachinePostDeployCommand(many=True, required=False)
