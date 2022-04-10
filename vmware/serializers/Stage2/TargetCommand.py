from rest_framework import serializers


class Stage2TargetCommandSerializer(serializers.Serializer):
    id_target = serializers.IntegerField(required=False)
    command = serializers.CharField(required=True, max_length=64, allow_blank=True)
    args = serializers.JSONField(required=True)
    sequence = serializers.IntegerField(required=True)
