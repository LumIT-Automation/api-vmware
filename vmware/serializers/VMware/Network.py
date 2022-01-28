from rest_framework import serializers

class VMwareNetworkSerializer(serializers.Serializer):
    class VMwareNetworkInnerSerializer(serializers.Serializer):
        class VMwareNetworkAttachedHostsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=False)
            name = serializers.CharField(max_length=255, required=False)
            vlanId = serializers.IntegerField(required=False)

        class VMwareNetworkInfoSerializer(serializers.Serializer):
            name = serializers.CharField(max_length=255, required=False)
            accessible = serializers.BooleanField(required=False)
            vlanId = serializers.IntegerField(required=False)

        configuredHosts = VMwareNetworkAttachedHostsSerializer(many=True)
        networkInfo = VMwareNetworkInfoSerializer(required=False)

    data = VMwareNetworkInnerSerializer(required=True)
