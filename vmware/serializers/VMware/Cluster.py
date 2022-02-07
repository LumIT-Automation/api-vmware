from rest_framework import serializers

from vmware.serializers.VMware.Datastore import VMwareDatastoreInnerSerializer


class VMwareClusterInnerSerializer(serializers.Serializer):
    class VMwareClusterItemsSerializer(serializers.Serializer):
        moId = serializers.CharField(max_length=64, required=True)
        name = serializers.CharField(max_length=255, required=False)

    class VMwareClusterNetworksSerializer(serializers.Serializer):
        moId = serializers.CharField(max_length=64, required=True)
        name = serializers.CharField(max_length=255, required=False)
        accessible = serializers.BooleanField(required=False)
        type = serializers.CharField(max_length=15, required=True)

    assetId = serializers.CharField(max_length=64, required=True)
    moId = serializers.CharField(max_length=255, required=False)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    hosts = VMwareClusterItemsSerializer(many=True, required=False)
    datastores = VMwareDatastoreInnerSerializer(many=True, required=False)
    networks = VMwareClusterNetworksSerializer(many=True, required=False)

class VMwareClusterSerializer(serializers.Serializer):
    data = VMwareClusterInnerSerializer(required=True)
