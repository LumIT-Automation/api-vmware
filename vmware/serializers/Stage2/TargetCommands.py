from rest_framework import serializers

from vmware.serializers.Stage2.TargetCommand import Stage2TargetCommandSerializer


class Stage2TargetCommandsSerializer(serializers.Serializer):
    items = Stage2TargetCommandSerializer(many=True)
