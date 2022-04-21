from rest_framework import serializers


class Stage2TargetCommandSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    id_target = serializers.IntegerField(required=False)
    command = serializers.CharField(required=True, max_length=64, allow_blank=True)
    user_args = serializers.JSONField(required=True)
