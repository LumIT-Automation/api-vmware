from rest_framework import serializers


class VMwareNetworksSerializer(serializers.Serializer):
    class VMwareNetworksInnerSerializer(serializers.Serializer):
        class VMwareNetworksItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        items = VMwareNetworksItemsSerializer(many=True)

    data = VMwareNetworksInnerSerializer(required=True)
