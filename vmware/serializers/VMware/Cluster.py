from rest_framework import serializers

from vmware.serializers.VMware.Datastore import VMwareDatastoreSerializer
from vmware.serializers.VMware.Network import VMwareNetworkSerializer


class VMwareClusterSerializer(serializers.Serializer):
    class VMwareClusterItemsSerializer(serializers.Serializer):
        moId = serializers.CharField(max_length=64, required=True)
        name = serializers.CharField(max_length=255, required=False)

    assetId = serializers.CharField(max_length=64, required=True)
    moId = serializers.CharField(max_length=255, required=False)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    hosts = VMwareClusterItemsSerializer(many=True, required=False, allow_null=True)
    datastores = VMwareDatastoreSerializer(many=True, required=False, allow_null=True)
    networks = VMwareNetworkSerializer(many=True, required=False, allow_null=True)
