from rest_framework import serializers

class VMwareNetworkSerializer(serializers.Serializer):
    class VMwareNetworkInnerSerializer(serializers.Serializer):
        class VMwareNetworkAttachedHostsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=False)
            name = serializers.CharField(max_length=255, required=False)
            vlanId = serializers.CharField(max_length=15, required=False)

        assetId = serializers.IntegerField(required=True)
        moId = serializers.CharField(max_length=64, required=False)
        name = serializers.CharField(max_length=255, required=False)
        accessible = serializers.BooleanField(required=False)
        type = serializers.CharField(max_length=15, required=False, allow_blank=True)
        configuredHosts = VMwareNetworkAttachedHostsSerializer(many=True)

    data = VMwareNetworkInnerSerializer(required=True)
