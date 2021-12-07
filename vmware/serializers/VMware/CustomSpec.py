from rest_framework import serializers

class VMwareCustomizationSpecEditSerializer(serializers.Serializer):

    class VMwareCustomizationSpecEditInnerSerializer(serializers.Serializer):
        ip = serializers.CharField(max_length=64, required=True)
        netMask = serializers.CharField(max_length=64, required=False)
        gw = serializers.CharField(max_length=64, required=False)
        dns1 = serializers.CharField(max_length=64, required=False)
        dns2 = serializers.CharField(max_length=64, required=False)
        hostName = serializers.CharField(max_length=127, required=False)
        domainName = serializers.CharField(max_length=255, required=False)
        timeZone = serializers.CharField(max_length=127, required=False)

    data = VMwareCustomizationSpecEditInnerSerializer(required=True)

