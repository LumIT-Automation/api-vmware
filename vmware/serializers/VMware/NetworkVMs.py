from rest_framework import serializers


class VMwareNetworkVMsSerializer(serializers.Serializer):
    class VMwareNetworkVMsItemsSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, allow_blank=True, max_length=255)
        moId = serializers.CharField(required=False, max_length=64)
        ipList = serializers.DictField(child=serializers.ListField(child=serializers.CharField(max_length=64), required=False), required=False)

    items = VMwareNetworkVMsItemsSerializer(many=True)
