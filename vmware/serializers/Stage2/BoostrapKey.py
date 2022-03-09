from rest_framework import serializers


class Stage2BootstrapKeySerializer(serializers.Serializer):
    class Stage2BootstrapKeyInnerSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        priv_key = serializers.CharField(max_length=8192, required=False, allow_blank=True)
        comment = serializers.CharField(max_length=1024, required=False, allow_blank=True)

    data = Stage2BootstrapKeyInnerSerializer(required=True)
