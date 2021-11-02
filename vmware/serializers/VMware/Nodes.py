from rest_framework import serializers


class VMwareNodesSerializer(serializers.Serializer):
    class VMwareNodesInnerSerializer(serializers.Serializer):
        class VMwareNodesItemsSerializer(serializers.Serializer):
            class VMwareNodesItemsFQDNSerializer(serializers.Serializer):
                addressFamily = serializers.CharField(max_length=255, required=True)
                autopopulate = serializers.CharField(max_length=255, required=True)
                interval = serializers.CharField(max_length=255, required=True)
                downInterval = serializers.IntegerField(required=True)

            name = serializers.CharField(max_length=255, required=True)
            vmFolder = serializers.CharField(max_length=255, required=True)
            fullPath = serializers.CharField(max_length=255, required=True)
            generation = serializers.IntegerField(required=True)
            selfLink = serializers.CharField(max_length=255, required=True)
            address = serializers.IPAddressField(required=True)
            connectionLimit = serializers.IntegerField(required=True)
            dynamicRatio = serializers.IntegerField(required=True)
            ephemeral = serializers.CharField(max_length=255, required=True)
            fqdn = VMwareNodesItemsFQDNSerializer(required=True)
            logging = serializers.CharField(max_length=255, required=True)
            monitor = serializers.CharField(max_length=255, required=True)
            rateLimit = serializers.CharField(max_length=255, required=True)
            ratio = serializers.IntegerField(required=True)
            session = serializers.CharField(max_length=255, required=True)
            state = serializers.CharField(max_length=255, required=True)

        items = VMwareNodesItemsSerializer(many=True)

    data = VMwareNodesInnerSerializer(required=True)
