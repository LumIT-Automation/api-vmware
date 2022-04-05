from rest_framework import serializers


class Stage2AddMountPointSerializer(serializers.Serializer):
    class Stage2AddMountPointShellVarsSerializer(serializers.Serializer):
        mountFolder = serializers.CharField(max_length=255, required=True)
        vgName = serializers.CharField(max_length=63, required=True)
        lvName = serializers.CharField(max_length=63, required=True)
        lvSize = serializers.IntegerField(required=True)
        filesystem = serializers.CharField(max_length=63, required=True)

    sudo = serializers.BooleanField(required=False)
    shellVars = Stage2AddMountPointShellVarsSerializer(required=True)
