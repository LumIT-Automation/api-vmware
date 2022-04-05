from rest_framework import serializers

from vmware.serializers.Stage2.Target import Stage2TargetSerializer


class Stage2TargetsSerializer(serializers.Serializer):
    items = Stage2TargetSerializer(many=True)
