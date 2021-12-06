from rest_framework import serializers


class VMwareHostSystemsSerializer(serializers.Serializer):
    class VMwareHostSystemsInnerSerializer(serializers.Serializer):
        class VMwareHostSystemsItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        items = VMwareHostSystemsItemsSerializer(many=True)

    data = VMwareHostSystemsInnerSerializer(required=True)
