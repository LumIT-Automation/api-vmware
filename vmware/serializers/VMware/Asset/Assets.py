from rest_framework import serializers


class VMwareAssetsSerializer(serializers.Serializer):
    class VMwareAssetsInnerSerializer(serializers.Serializer):
        class VMwareAssestItems(serializers.Serializer):
            id = serializers.IntegerField(required=True) # @todo: only valid data.
            address = serializers.CharField(max_length=64, required=True) # @todo: only valid data.
            fqdn = serializers.CharField(max_length=255, required=True) # @todo: only valid data.
            baseurl = serializers.CharField(max_length=255, required=True)
            tlsverify = serializers.IntegerField(required=True)
            datacenter = serializers.CharField(max_length=255, required=True)
            environment = serializers.CharField(max_length=255, required=True)
            position = serializers.CharField(max_length=255, required=True)

        items = VMwareAssestItems(many=True)

    data = VMwareAssetsInnerSerializer(required=True)
