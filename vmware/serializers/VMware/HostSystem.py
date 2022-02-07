from rest_framework import serializers

class VMwareHostSystemSerializer(serializers.Serializer):
    class VMwareHostSystemInnerSerializer(serializers.Serializer):
        class VMwareHostSystemDatastoresSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=255, required=False)
            name = serializers.CharField(max_length=255, required=False)
            url = serializers.CharField(max_length=1024, required=False)
            freeSpace = serializers.IntegerField(required=True)
            maxFileSize = serializers.IntegerField(required=True)
            maxVirtualDiskCapacity = serializers.IntegerField(required=True, allow_null=True)
            type = serializers.CharField(max_length=64, required=False)
            capacity = serializers.IntegerField(required=True)
            majorVersion = serializers.IntegerField(required=False)
            ssd = serializers.BooleanField(required=False)
            local = serializers.BooleanField(required=False, allow_null=True)
            multipleHostAccess = serializers.BooleanField(required=False)

        class VMwareHostSystemNetworksSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=False)
            name = serializers.CharField(max_length=255, required=False, allow_blank=True)
            vlanId = serializers.CharField(max_length=15, required=False)

        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(max_length=64, required=False)
        name = serializers.CharField(max_length=255, required=False, allow_blank=True)
        datastores = VMwareHostSystemDatastoresSerializer(many=True)
        networks = VMwareHostSystemNetworksSerializer(many=True)


    data = VMwareHostSystemInnerSerializer(required=True)
