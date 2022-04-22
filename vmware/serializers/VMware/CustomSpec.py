from rest_framework import serializers


class VMwareCustomizationSpecSerializer(serializers.Serializer):
    class VMwareCustomizationSpecNetworkSerializer(serializers.Serializer):
        ip = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
        netMask = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
        gw = serializers.ListField(
            child=serializers.IPAddressField(required=False, allow_blank=True, allow_null=True), required=False, allow_null=True
        )

    assetId = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False, max_length=255)
    dns1 = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
    dns2 = serializers.IPAddressField(required=False, allow_blank=True, allow_null=True)
    hostName = serializers.CharField(required=False, max_length=127, allow_blank=True, allow_null=True)
    domainName = serializers.CharField(required=False, max_length=255, allow_blank=True, allow_null=True)
    timeZone = serializers.CharField(required=False, max_length=127, allow_blank=True, allow_null=True)

    network = VMwareCustomizationSpecNetworkSerializer(many=True, required=False)



class VMwareCustomizationSpecCloneSerializer(serializers.Serializer):
    destination = serializers.CharField(required=True, max_length=64)



class VMwareCustomizationSpecApplySerializer(serializers.Serializer):
    specName = serializers.CharField(required=True, max_length=64)
