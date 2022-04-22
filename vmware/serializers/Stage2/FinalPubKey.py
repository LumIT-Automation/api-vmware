from rest_framework import serializers


class Stage2FinalPubKeySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    pub_key = serializers.CharField(max_length=1024, required=True)
    comment = serializers.CharField(max_length=1024, required=True, allow_blank=True)
