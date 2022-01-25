from rest_framework import serializers

class VMwareDatacenterSerializer(serializers.Serializer):
    class VMwareDatacenterInnerSerializer(serializers.Serializer):
        class VMwareDatacenterItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        clusters = VMwareDatacenterItemsSerializer(many=True)

    data = VMwareDatacenterInnerSerializer(required=True)
