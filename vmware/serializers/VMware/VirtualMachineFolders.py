from rest_framework import serializers

from vmware.serializers.VMware.VirtualMachineFolder import VMwareVirtualMachineFolderSerializer


class VMwareVirtualMachinesFolderSerializer(serializers.Serializer):

    items = VMwareVirtualMachineFolderSerializer(many=True,required=True)

