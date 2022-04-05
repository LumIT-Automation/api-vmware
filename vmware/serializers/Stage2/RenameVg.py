from rest_framework import serializers


class Stage2RenamveVgSerializer(serializers.Serializer):
    class Stage2RenameVgShellVarsSerializer(serializers.Serializer):
        vgName =  serializers.CharField(max_length=64, required=True)

    sudo = serializers.BooleanField(required=False)
    shellVars = Stage2RenameVgShellVarsSerializer(required=True)
