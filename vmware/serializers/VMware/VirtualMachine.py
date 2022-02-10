from rest_framework import serializers

class VMwareVirtualMachineSerializer(serializers.Serializer):
    class VMwareVirtualMachineInnerSerializer(serializers.Serializer):

        class VMwareVirtualMachineDisksSerializer(serializers.Serializer):
            label = serializers.CharField(max_length=255, required=True)
            size = serializers.CharField(max_length=255, required=False)

        class VMwareVirtualMachineNetworkDevicesSerializer(serializers.Serializer):
            label = serializers.CharField(max_length=255, required=True)
            network = serializers.CharField(max_length=255, required=False)

        name = serializers.CharField(max_length=255, required=False)
        guestName = serializers.CharField(max_length=255, required=False)
        version = serializers.CharField(max_length=63,required=True)
        uuid = serializers.CharField(max_length=255, required=True)
        numCpu = serializers.IntegerField(required=True,allow_null=True)
        numCoresPerSocket = serializers.IntegerField(required=False)
        memoryMB = serializers.IntegerField(required=True)
        template = serializers.BooleanField(required=False)

        networkDevices = VMwareVirtualMachineNetworkDevicesSerializer(many=True, required=False, allow_null=True)
        diskDevices = VMwareVirtualMachineDisksSerializer(many=True, required=False, allow_null=True)

    data = VMwareVirtualMachineInnerSerializer(required=True)
