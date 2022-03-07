from rest_framework import serializers


class Stage2CommandRebootSerializer(serializers.Serializer):
    class Stage2CommandRebootInnerSerializer(serializers.Serializer):
        priv_key_id = serializers.IntegerField(required=True, allow_null=True)

    data = Stage2CommandRebootInnerSerializer(required=True)
