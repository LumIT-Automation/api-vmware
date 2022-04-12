from rest_framework import serializers


class Stage2CommandRunSerializer(serializers.Serializer):
    args = serializers.JSONField(required=False)
