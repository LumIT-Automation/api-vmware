from rest_framework import serializers

from vmware.serializers.VMware.Datastore import VMwareDatastoreSerializer
from vmware.serializers.VMware.Network import VMwareNetworkSerializer


class VMwareHostSystemSerializer(serializers.Serializer):
    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(max_length=64, required=False)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    datastores = VMwareDatastoreSerializer(many=True, required=False, allow_null=True)
    networks = VMwareNetworkSerializer(many=True, required=False, allow_null=True)
