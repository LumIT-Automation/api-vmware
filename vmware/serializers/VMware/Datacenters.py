from rest_framework import serializers


class VMwareDatacentersSerializer(serializers.Serializer):
    class VMwareDatacentersInnerSerializer(serializers.Serializer):
        class VMwareDatacentersItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        items = VMwareDatacentersItemsSerializer(many=True)

    data = VMwareDatacentersInnerSerializer(required=True)
