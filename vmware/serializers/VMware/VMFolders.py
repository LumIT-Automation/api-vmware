from rest_framework import serializers


class VMwareVMFoldersSerializer(serializers.Serializer):
    class VMwareVMFoldersInnerSerializer(serializers.Serializer):
        class VMwareVMFoldersItemsSerializer(serializers.Serializer):
            name = serializers.CharField(max_length=255, required=True)
            fullPath = serializers.CharField(max_length=255, required=True)
            generation = serializers.IntegerField(required=True)
            selfLink = serializers.CharField(max_length=255, required=True)
            defaultRouteDomain = serializers.IntegerField(required=True)

        items = VMwareVMFoldersItemsSerializer(many=True)

    data = VMwareVMFoldersInnerSerializer(required=True)
