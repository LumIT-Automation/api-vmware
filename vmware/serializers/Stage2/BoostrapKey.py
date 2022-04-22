from rest_framework import serializers


class Stage2BootstrapKeySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    priv_key = serializers.CharField(max_length=65535, required=True)
    pub_key = serializers.CharField(max_length=65535, required=False)
    comment = serializers.CharField(max_length=1024, required=True, allow_blank=True)
