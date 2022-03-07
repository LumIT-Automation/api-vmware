from rest_framework import serializers


class Stage2TargetsSerializer(serializers.Serializer):
    class Stage2TargetsInnerSerializer(serializers.Serializer):
        class Stage2TargetsItems(serializers.Serializer):
            id = serializers.IntegerField(required=True) # @todo: only valid data.
            address = serializers.CharField(max_length=64, required=True) # @todo: only valid data.
            port = serializers.CharField(max_length=64, required=True) # @todo: only valid data.
            api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)

        items = Stage2TargetsItems(many=True)

    data = Stage2TargetsInnerSerializer(required=True)
