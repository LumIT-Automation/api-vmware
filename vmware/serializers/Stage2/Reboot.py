from rest_framework import serializers


class Stage2CommandRebootSerializer(serializers.Serializer):
    class Stage2CommandRebootInnerSerializer(serializers.Serializer):
        priv_key_id = serializers.IntegerField(required=True, allow_null=True)
        username = serializers.CharField(max_length=64, required=False, allow_blank=True)

    data = Stage2CommandRebootInnerSerializer(required=True)
