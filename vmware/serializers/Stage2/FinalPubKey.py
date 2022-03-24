from rest_framework import serializers


class Stage2FinalPubKeySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    pub_key = serializers.CharField(max_length=1024, required=False, allow_blank=True)
    comment = serializers.CharField(max_length=1024, required=False, allow_blank=True)
