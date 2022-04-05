from rest_framework import serializers


class Stage2SshCommandSerializer(serializers.Serializer):
    sudo = serializers.BooleanField(required=False)
