from rest_framework import serializers


class Stage2SshRebootSerializer(serializers.Serializer):
    class Stage2SshRebootInnerSerializer(serializers.Serializer):
        priv_key_id = serializers.IntegerField(required=True, allow_null=True)
        username = serializers.CharField(max_length=64, required=False, allow_blank=True)

    data = Stage2SshRebootInnerSerializer(required=True)
