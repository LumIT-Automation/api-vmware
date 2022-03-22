from rest_framework import serializers


class Stage2BootstrapKeysSerializer(serializers.Serializer):
    class Stage2BootstrapKeysInnerSerializer(serializers.Serializer):
        class Stage2BootstrapKeysItems(serializers.Serializer):
            id = serializers.IntegerField(required=False)
            priv_key = serializers.CharField(max_length=8192, required=False, allow_blank=True)
            pub_key = serializers.CharField(max_length=1024, required=False, allow_blank=True)
            comment = serializers.CharField(max_length=1024, required=False, allow_blank=True)


        items = Stage2BootstrapKeysItems(many=True)

    data = Stage2BootstrapKeysInnerSerializer(required=True)
