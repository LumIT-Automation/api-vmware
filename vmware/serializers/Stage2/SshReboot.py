from rest_framework import serializers


class Stage2SshCommandSerializer(serializers.Serializer):
    class Stage2SshCommandInnerSerializer(serializers.Serializer):
        sudo = serializers.BooleanField(required=False)

    data = Stage2SshCommandInnerSerializer(required=True)
