from rest_framework import serializers


class VMwareNodeSerializer(serializers.Serializer):
    class VMwareNodeInnerSerializer(serializers.Serializer):
        class VMwareNodesItemFQDNSerializer(serializers.Serializer):
            addressFamily = serializers.CharField(max_length=255, required=False)
            autopopulate = serializers.CharField(max_length=255, required=False)
            interval = serializers.CharField(max_length=255, required=False)
            downInterval = serializers.IntegerField(required=False)

        name = serializers.CharField(max_length=255, required=True)
        vmFolder = serializers.CharField(max_length=255, required=False)
        fullPath = serializers.CharField(max_length=255, required=False)
        generation = serializers.IntegerField(required=False)
        selfLink = serializers.CharField(max_length=255, required=False)
        address = serializers.IPAddressField(required=True)
        connectionLimit = serializers.IntegerField(required=False)
        dynamicRatio = serializers.IntegerField(required=False)
        ephemeral = serializers.CharField(max_length=255, required=False)
        fqdn = VMwareNodesItemFQDNSerializer(required=False)
        logging = serializers.CharField(max_length=255, required=False)
        monitor = serializers.CharField(max_length=255, required=False)
        rateLimit = serializers.CharField(max_length=255, required=False)
        ratio = serializers.IntegerField(required=False)
        session = serializers.CharField(max_length=255, required=False)
        state = serializers.CharField(max_length=255, required=False) # do not modify.

    data = VMwareNodeInnerSerializer(required=True)
