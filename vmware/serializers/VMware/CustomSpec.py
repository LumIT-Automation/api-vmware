from rest_framework import serializers


class VMwareCustomizationSpecSerializer(serializers.Serializer):
    class VMwareCustomizationSpecNetworkSerializer(serializers.Serializer):
        ip = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
        netMask = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        gw = serializers.ListField(
            child=serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
        )

    assetId = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    dns1 = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
    dns2 = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
    hostName = serializers.CharField(max_length=127, required=False, allow_blank=True, allow_null=True)
    domainName = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    timeZone = serializers.CharField(max_length=127, required=False, allow_blank=True, allow_null=True)
    network = VMwareCustomizationSpecNetworkSerializer(many=True)


