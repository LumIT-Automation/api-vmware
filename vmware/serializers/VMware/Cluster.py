from rest_framework import serializers

from vmware.serializers.VMware.Datastore import VMwareDatastoreInnerSerializer


class VMwareClusterInnerSerializer(serializers.Serializer):
    class VMwareClusterItemsSerializer(serializers.Serializer):
        moId = serializers.CharField(max_length=64, required=True)
        name = serializers.CharField(max_length=255, required=False)

    assetId = serializers.CharField(max_length=64, required=True)
    moId = serializers.CharField(max_length=255, required=False)

    hosts = VMwareClusterItemsSerializer(many=True, required=False)
    datastores = VMwareDatastoreInnerSerializer(many=True, required=False)
    networks = VMwareClusterItemsSerializer(many=True, required=False)

class VMwareClusterSerializer(serializers.Serializer):
    data = VMwareClusterInnerSerializer(required=True)
