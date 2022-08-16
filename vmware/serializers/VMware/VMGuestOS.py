from rest_framework import serializers


class VMwareVMGuestOSSerializer(serializers.Serializer):

    class VMwareVMGuestOSToolsSerializer(serializers.Serializer):
        version = serializers.IntegerField(required=False)
        type = serializers.CharField(required=False, allow_blank=True, max_length=64)
        status = serializers.CharField(required=False, allow_blank=True, max_length=64)
        runningStatus = serializers.CharField(required=False, allow_blank=True, max_length=64)

    class VMwareVMGuestOSDnsSerializer(serializers.Serializer):
        domain = serializers.CharField(required=False, allow_blank=True, max_length=255)
        searchDomain = serializers.ListField(child=serializers.CharField(max_length=255), required=False)
        dnsList = serializers.ListField(child=serializers.CharField(max_length=64), required=False)

    hostname = serializers.CharField(required=False, allow_blank=True, max_length=255)
    guestOS = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    guestOSFamily = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    vmTools = VMwareVMGuestOSToolsSerializer(required=False)
    dnsConfig = VMwareVMGuestOSDnsSerializer(required=False)
    network = serializers.DictField(child=serializers.ListField(child=serializers.CharField(max_length=64), required=False))



class VMwareVMGuestOSCustomizeSerializer(serializers.Serializer):
    specName = serializers.CharField(required=True, max_length=64)
