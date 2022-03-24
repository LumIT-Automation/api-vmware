from rest_framework import serializers

from vmware.serializers.Stage2.FinalPubKey import Stage2FinalPubKeySerializer


class Stage2FinalPubKeysSerializer(serializers.Serializer):
    class Stage2FinalPubKeysInnerSerializer(serializers.Serializer):
        items = Stage2FinalPubKeySerializer(many=True)

    data = Stage2FinalPubKeysInnerSerializer()
