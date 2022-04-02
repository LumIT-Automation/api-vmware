from rest_framework import serializers

from vmware.serializers.VMware.Cluster import VMwareClusterSerializer
from vmware.serializers.VMware.HostSystem import VMwareHostSystemSerializer


class VMwareDatacenterSerializer(serializers.Serializer):
    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(required=True, max_length=64)
    name = serializers.CharField(required=True, max_length=255)

    clusters = VMwareClusterSerializer(many=True, required=False, allow_null=True)
    standalone_hosts = VMwareHostSystemSerializer(many=True, required=False, allow_null=True)
