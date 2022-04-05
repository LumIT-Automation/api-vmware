from rest_framework import serializers


class Stage2TargetCommandSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    id_target = serializers.IntegerField(required=False)
    command = serializers.CharField(required=True, max_length=64, allow_blank=True)
    args = serializers.CharField(required=False, max_length=8192, allow_blank=True)
