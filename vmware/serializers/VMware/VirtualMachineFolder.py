from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField


class VMwareVirtualMachineFolderSerializer(serializers.Serializer):
    class VMwareVirtualMachineBriefSerializer(serializers.Serializer):
        moId = serializers.CharField(max_length=255, required=False)
        name = serializers.CharField(max_length=255, required=False)

    assetId = serializers.IntegerField(required=False)
    moId = serializers.CharField(max_length=255, required=True)
    name = serializers.CharField(max_length=255, required=False)
    folders = serializers.ListField(child=RecursiveField(), required=False)
    virtualmachines = VMwareVirtualMachineBriefSerializer(required=False, many=True)



class VMwareVirtualMachineFolderParentListSerializer(serializers.Serializer):
    data = serializers.ListField(
        child=serializers.CharField(max_length=64), required=False
    )
