from rest_framework import serializers

class VMwareDatastoreSerializer(serializers.Serializer):
    class VMwareDatastoreInnerSerializer(serializers.Serializer):
        class VMwareDatastoreAttachedHostsSerializer(serializers.Serializer):
            moId = serializers.CharField(max_length=64, required=True)
            name = serializers.CharField(max_length=255, required=False)
            vlanId = serializers.IntegerField(required=True)

        class VMwareDatastoreInfoSerializer(serializers.Serializer):
            name = serializers.CharField(max_length=255, required=False)
            accessible = serializers.BooleanField(required=False)

        configuredHosts = VMwareDatastoreAttachedHostsSerializer(many=True)
        networkInfo = VMwareDatastoreInfoSerializer(required=False)

    data = VMwareDatastoreInnerSerializer(required=True)
