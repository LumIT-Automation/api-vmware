from rest_framework import serializers


class VMwareNetworkVMsSerializer(serializers.Serializer):
    class VMwareNetworkVMsItemsSerializer(serializers.Serializer):
        class  VMwareNetworkVMsIpListSerializer(serializers.Serializer):
            pgName = serializers.CharField(required=False, allow_blank=True, max_length=255)
            ipAddress = serializers.ListField(child=serializers.IPAddressField(allow_blank=True, allow_null=True), required=False)

        name = serializers.CharField(required=False, allow_blank=True, max_length=255)
        moId = serializers.CharField(required=False, max_length=64)
        ipList = VMwareNetworkVMsIpListSerializer(many=True, required=False)

    items = VMwareNetworkVMsItemsSerializer(many=True)
