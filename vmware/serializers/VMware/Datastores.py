from rest_framework import serializers


class VMwareDatastoresSerializer(serializers.Serializer):
    class VMwareDatastoresInnerSerializer(serializers.Serializer):
        class VMwareDatastoresItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        items = VMwareDatastoresItemsSerializer(many=True)

    data = VMwareDatastoresInnerSerializer(required=True)
