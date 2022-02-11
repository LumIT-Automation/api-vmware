from rest_framework import serializers


class VMwareDeployTemplateSerializer(serializers.Serializer):
    class VMwareDeployTemplateInnerSerializer(serializers.Serializer):
        vmName = serializers.CharField(max_length=255, required=True)
        datacenterId = serializers.CharField(max_length=64, required=True)
        clusterId = serializers.CharField(max_length=64, required=True)
        datastoreId = serializers.CharField(max_length=64, required=True)
        networkId = serializers.CharField(max_length=64, required=True)
        vmFolderId = serializers.CharField(max_length=64, required=True)
        powerOn = serializers.BooleanField(required=False)

    data = VMwareDeployTemplateInnerSerializer(required=True)
