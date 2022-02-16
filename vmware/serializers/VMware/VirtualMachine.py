from rest_framework import serializers


class VMwareVirtualMachineSerializer(serializers.Serializer):
    class VMwareVirtualMachineDisksSerializer(serializers.Serializer):
        datastoreMoId = serializers.CharField(max_length=255, required=False)
        disk = serializers.CharField(max_length=255, required=True)
        size = serializers.CharField(max_length=255, required=False)

    class VMwareVirtualMachineNetworkDevicesSerializer(serializers.Serializer):
        networkMoId = serializers.CharField(max_length=255, required=False)
        label = serializers.CharField(max_length=255, required=True)

    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(max_length=255, required=False)
    name = serializers.CharField(max_length=255, required=False)
    guestName = serializers.CharField(max_length=255, required=False)
    version = serializers.CharField(max_length=63, required=True)
    uuid = serializers.CharField(max_length=255, required=True)
    numCpu = serializers.IntegerField(required=True, allow_null=True)
    numCoresPerSocket = serializers.IntegerField(required=False)
    memoryMB = serializers.IntegerField(required=True)
    template = serializers.BooleanField(required=False)
    notes = serializers.CharField(max_length=2048, required=False)

    networkDevices = VMwareVirtualMachineNetworkDevicesSerializer(many=True, required=False, allow_null=True)
    diskDevices = VMwareVirtualMachineDisksSerializer(many=True, required=False, allow_null=True)



class VMwareVirtualMachineModifySerializer(serializers.Serializer):
    class VMwareVirtualMachineModifyInnerSerializer(serializers.Serializer):
        diskLabel = serializers.CharField(max_length=63, required=False)
        diskSizeMB = serializers.IntegerField(required=False)
        numCpu = serializers.IntegerField(required=False)
        numCoresPerSocket = serializers.IntegerField(required=False)
        memoryMB = serializers.IntegerField(required=False)
        notes = serializers.CharField(max_length=2048, required=False)

    data = VMwareVirtualMachineModifyInnerSerializer(required=True)
