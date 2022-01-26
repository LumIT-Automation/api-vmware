from rest_framework import serializers

from vmware.serializers.VMware.Cluster import VMwareClusterInnerSerializer


class VMwareDatacenterSerializer(serializers.Serializer):
    class VMwareDatacenterInnerSerializer(serializers.Serializer):
        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(max_length=64, required=True)
        name = serializers.CharField(max_length=255, required=False)
        clusters = VMwareClusterInnerSerializer(many=True)

    data = VMwareDatacenterInnerSerializer(required=True)
