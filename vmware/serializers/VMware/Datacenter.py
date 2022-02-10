from rest_framework import serializers

from vmware.serializers.VMware.Cluster import VMwareClusterSerializer


class VMwareDatacenterSerializer(serializers.Serializer):
    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(max_length=64, required=True)
    name = serializers.CharField(max_length=255, required=False)

    clusters = VMwareClusterSerializer(many=True, required=False, allow_null=True)
