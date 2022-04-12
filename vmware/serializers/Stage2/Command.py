from rest_framework import serializers


class Stage2CommandSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    command = serializers.CharField(required=True, max_length=65535)
    template_args = serializers.JSONField(required=True)
