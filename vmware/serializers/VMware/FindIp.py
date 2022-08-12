from rest_framework import serializers


class VMwareFindIpSerializer(serializers.Serializer):
    class VMwareFindIpItemsSerializer(serializers.Serializer):
        moId = serializers.CharField(required=False, max_length=64)
        name = serializers.CharField(required=False, max_length=255)

    items = VMwareFindIpItemsSerializer(many=True)