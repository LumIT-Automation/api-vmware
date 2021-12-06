from rest_framework import serializers

class VMwareHostSystemSerializer(serializers.Serializer):
    class VMwareHostSystemInnerSerializer(serializers.Serializer):
        class VMwareHostSystemItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=False)
            name = serializers.CharField(max_length=255, required=False)

        datastores = VMwareHostSystemItemsSerializer(many=True)
        networks = VMwareHostSystemItemsSerializer(many=True)

    data = VMwareHostSystemInnerSerializer(required=True)
