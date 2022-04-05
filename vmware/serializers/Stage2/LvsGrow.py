from rest_framework import serializers


class Stage2LvsGrowSerializer(serializers.Serializer):
    class Stage2LvsGrowShellVarsSerializer(serializers.Serializer):
        vgName = serializers.CharField(max_length=64, required=True)
        lvName = serializers.CharField(max_length=64, required=True)
        grow_100 = serializers.BooleanField(required=True)
        totSize = serializers.IntegerField(required=True)
        growSize = serializers.IntegerField(required=True)

    sudo = serializers.BooleanField(required=False)
    shellVars = Stage2LvsGrowShellVarsSerializer(required=True)
