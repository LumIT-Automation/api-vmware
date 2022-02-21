from rest_framework import serializers


class VMwareCustomizationSpecSerializer(serializers.Serializer):
    class VMwareCustomizationSpecNetworkSerializer(serializers.Serializer):
        ip = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        netMask = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        gw = serializers.ListField(
            child=serializers.CharField(max_length=255, required=False)
        )

    assetId = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    dns1 = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    dns2 = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    hostName = serializers.CharField(max_length=127, required=False, allow_blank=True, allow_null=True)
    domainName = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    timeZone = serializers.CharField(max_length=127, required=False, allow_blank=True, allow_null=True)
    network = VMwareCustomizationSpecNetworkSerializer(many=True)

