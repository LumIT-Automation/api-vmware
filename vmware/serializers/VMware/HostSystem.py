from rest_framework import serializers


class VMwareHostSystemSerializer(serializers.Serializer):
    class _VMwareDatastoreSerializer(serializers.Serializer):
        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(max_length=255, required=False)
        name = serializers.CharField(max_length=255, required=False)
        url = serializers.CharField(max_length=1024, required=False)
        freeSpace = serializers.IntegerField(required=True)
        maxFileSize = serializers.IntegerField(required=True)
        maxVirtualDiskCapacity = serializers.IntegerField(required=True, allow_null=True)
        vmfsType = serializers.CharField(max_length=64, required=False)
        capacity = serializers.IntegerField(required=True)
        majorVersion = serializers.IntegerField(required=False, allow_null=True)
        ssd = serializers.BooleanField(required=False, allow_null=True)
        local = serializers.BooleanField(required=False, allow_null=True)
        multipleHostAccess = serializers.BooleanField(required=False)

    class _VMwareNetworkSerializer(serializers.Serializer):
        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(max_length=64, required=False)
        name = serializers.CharField(max_length=255, required=False)
        accessible = serializers.BooleanField(required=False)
        type = serializers.CharField(max_length=15, required=False, allow_blank=True)
        vlanId = serializers.CharField(max_length=15, required=False, allow_blank=True)

    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(max_length=64, required=False)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    datastores = _VMwareDatastoreSerializer(many=True, required=False, allow_null=True) # avoiding circular input, @todo, is there a better way?
    networks = _VMwareNetworkSerializer(many=True, required=False, allow_null=True)
