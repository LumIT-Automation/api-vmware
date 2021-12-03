from rest_framework import serializers

class VMwareClusterSerializer(serializers.Serializer):
    class VMwareClusterInnerSerializer(serializers.Serializer):
        class VMwareClusterItemsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)

        hosts = VMwareClusterItemsSerializer(many=True)
        datastores = VMwareClusterItemsSerializer(many=True)
        networks = VMwareClusterItemsSerializer(many=True)

    data = VMwareClusterInnerSerializer(required=True)
