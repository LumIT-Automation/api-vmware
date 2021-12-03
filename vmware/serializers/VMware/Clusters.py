from rest_framework import serializers


class VMwareClustersSerializer(serializers.Serializer):
    class VMwareClustersInnerSerializer(serializers.Serializer):
        class VMwareClustersItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        items = VMwareClustersItemsSerializer(many=True)

    data = VMwareClustersInnerSerializer(required=True)
