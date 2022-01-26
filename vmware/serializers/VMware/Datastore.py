from rest_framework import serializers

class VMwareDatastoreSerializer(serializers.Serializer):
    class VMwareDatastoreInnerSerializer(serializers.Serializer):
        class VMwareDatastoreAttachedHostsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(max_length=255, required=False)
        name = serializers.CharField(max_length=255, required=False)
        url = serializers.CharField(max_length=1024, required=False)
        freeSpace = serializers.IntegerField(required=True)
        maxFileSize = serializers.IntegerField(required=True)
        maxVirtualDiskCapacity = serializers.IntegerField(required=True,allow_null=True)
        type = serializers.CharField(max_length=64, required=False)
        capacity = serializers.IntegerField(required=True)
        majorVersion = serializers.IntegerField(required=False)
        ssd = serializers.BooleanField(required=False)
        local = serializers.BooleanField(required=False,allow_null=True)
        multipleHostAccess = serializers.BooleanField(required=False)

        attachedHosts = VMwareDatastoreAttachedHostsSerializer(many=True)

    data = VMwareDatastoreInnerSerializer(required=True)
