from rest_framework import serializers


class Stage2TargetSerializer(serializers.Serializer):
    class Stage2TargetInnerSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)  # @todo: only valid data.
        address = serializers.CharField(max_length=64, required=True)  # @todo: only valid data.
        port = serializers.CharField(max_length=64, required=True)  # @todo: only valid data.
        api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)
        id_bootstrap_key = serializers.IntegerField(required=False)
        username = serializers.CharField(max_length=64, required=False)
        password = serializers.CharField(max_length=64, required=False)

    data = Stage2TargetInnerSerializer(required=True)
