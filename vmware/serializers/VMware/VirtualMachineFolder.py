from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField


class VMwareVirtualMachineFolderSerializer(serializers.Serializer):
    class VMwareVirtualMachineBriefSerializer(serializers.Serializer):
        moId = serializers.CharField(required=False, max_length=255)
        name = serializers.CharField(required=False, max_length=255)

    assetId = serializers.IntegerField(required=False)
    moId = serializers.CharField(required=True, max_length=255)
    name = serializers.CharField(required=False, max_length=255)
    children = serializers.ListField(child=RecursiveField(), required=False)
    virtualmachines = VMwareVirtualMachineBriefSerializer(required=False, many=True)



class VMwareVirtualMachineFolderParentListSerializer(serializers.Serializer):
    data = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False
    )
