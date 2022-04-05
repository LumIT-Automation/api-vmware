from rest_framework import serializers


class Stage2ResizeLastPartitionSerializer(serializers.Serializer):
    class StageResizeLastPartitionShellVarsSerializer(serializers.Serializer):
        diskDevice = serializers.CharField(max_length=64, required=True)

    sudo = serializers.BooleanField(required=False)
    shellVars = StageResizeLastPartitionShellVarsSerializer(required=True)
