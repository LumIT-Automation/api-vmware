from rest_framework import serializers

from vmware.serializers.Stage2.Command import Stage2CommandSerializer


class Stage2CommandsSerializer(serializers.Serializer):
    items = Stage2CommandSerializer(many=True)
