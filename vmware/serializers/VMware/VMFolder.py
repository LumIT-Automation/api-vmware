from rest_framework import serializers

class VMwareVMFolderSerializer(serializers.Serializer):
    class VMwareVMFolderInnerSerializer(serializers.Serializer):
        class VMwareVMFolderItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        class VMwareVAppItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        vmList = VMwareVMFolderItemsSerializer(many=True)
        vAppList = VMwareVAppItemsSerializer(many=True)

    data = VMwareVMFolderInnerSerializer(required=True)



class VMwareVMFolderParentListSerializer(serializers.Serializer):
    data = serializers.ListField(
        child = serializers.CharField(max_length=255, required=False)
    )

