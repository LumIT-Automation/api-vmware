from rest_framework import serializers


class VMwareHostSystemSerializer(serializers.Serializer):
    class _VMwareDatastoreSerializer(serializers.Serializer):
        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(required=False, max_length=255)
        name = serializers.CharField(required=False, max_length=255)
        url = serializers.CharField(required=False, max_length=1024)
        freeSpace = serializers.IntegerField(required=True)
        maxFileSize = serializers.IntegerField(required=True)
        maxVirtualDiskCapacity = serializers.IntegerField(required=True, allow_null=True)
        vmfsType = serializers.CharField(required=False, max_length=64)
        capacity = serializers.IntegerField(required=True)
        majorVersion = serializers.IntegerField(required=False, allow_null=True)
        ssd = serializers.BooleanField(required=False, allow_null=True)
        local = serializers.BooleanField(required=False, allow_null=True)
        multipleHostAccess = serializers.BooleanField(required=False)

    class _VMwareNetworkSerializer(serializers.Serializer):
        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(required=False, max_length=64)
        name = serializers.CharField(required=False, max_length=255)
        accessible = serializers.BooleanField(required=False)
        type = serializers.CharField(required=False, max_length=15, allow_blank=True)
        vlanId = serializers.CharField(required=False, max_length=15, allow_blank=True)

    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(required=True, max_length=64)
    name = serializers.CharField(required=True, max_length=255, allow_blank=True)

    datastores = _VMwareDatastoreSerializer(many=True, required=False, allow_null=True) # avoiding circular input, @todo, is there a better way?
    networks = _VMwareNetworkSerializer(many=True, required=False, allow_null=True)
