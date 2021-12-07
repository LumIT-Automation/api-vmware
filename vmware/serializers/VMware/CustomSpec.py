from rest_framework import serializers

class VMwareCustomizationSpecSerializer(serializers.Serializer):

    class VMwareCustomizationSpecInnerSerializer(serializers.Serializer):

        class VMwareCustomizationSpecGwSerializer(serializers.ListField):
            child=serializers.CharField(max_length=64, required=False)

        ip = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        netMask = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        gw = VMwareCustomizationSpecGwSerializer(required=False)
        dns1 = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        dns2 = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        hostName = serializers.CharField(max_length=127, required=False, allow_blank=True, allow_null=True)
        domainName = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
        timeZone = serializers.CharField(max_length=127, required=False, allow_blank=True, allow_null=True)

    data = VMwareCustomizationSpecInnerSerializer(required=True)

