from rest_framework import serializers

from vmware.serializers.VMware.HostSystem import VMwareHostSystemSerializer
from vmware.serializers.VMware.Datastore import VMwareDatastoreSerializer
from vmware.serializers.VMware.Network import VMwareNetworkSerializer


class VMwareClusterSerializer(serializers.Serializer):
    assetId = serializers.CharField(required=True, max_length=64)
    moId = serializers.CharField(required=True, max_length=255)
    name = serializers.CharField(required=True, max_length=255, allow_blank=True)

    hosts = VMwareHostSystemSerializer(many=True, required=False, allow_null=True)
    datastores = VMwareDatastoreSerializer(many=True, required=False, allow_null=True)
    networks = VMwareNetworkSerializer(many=True, required=False, allow_null=True)
