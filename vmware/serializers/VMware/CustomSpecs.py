from rest_framework import serializers

class VMwareCustomizationSpecsSerializer(serializers.Serializer):
    class VMwareCustomizationSpecsInnerSerializer(serializers.Serializer):
        items = serializers.ListField(
            child = serializers.CharField(max_length=255, required=False)
        )

    data = VMwareCustomizationSpecsInnerSerializer(required=True)



class VMwareCustomizationSpecCloneSerializer(serializers.Serializer):
    class VMwareCustomizationSpecCloneInnerSerializer(serializers.Serializer):
        sourceSpec = serializers.CharField(max_length=64, required=True)
        newSpec = serializers.CharField(max_length=255, required=False)

    data = VMwareCustomizationSpecCloneInnerSerializer(required=True)

