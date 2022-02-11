from rest_framework import serializers

from vmware.serializers.VMware.VirtualMachine import VMwareVirtualMachineSerializer


class VMwareVirtualMachinesSerializer(serializers.Serializer):
    items = VMwareVirtualMachineSerializer(many=True)
