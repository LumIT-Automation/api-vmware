from rest_framework import serializers


class Stage2TargetAddFinalPubKeysSerializer(serializers.Serializer):
    class Stage2TargetAddFinalPubKeysInnerSerializer(serializers.Serializer):
        sudo = serializers.BooleanField(required=False)

        keyIds = serializers.ListField(
            child=serializers.IntegerField(required=False),
            required=False
        )

    data = Stage2TargetAddFinalPubKeysInnerSerializer(required=True)
