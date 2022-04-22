from rest_framework import serializers


class HistorySerializer(serializers.Serializer):
    class HistoryItemsSerializer(serializers.Serializer):
        username = serializers.CharField(required=True, max_length=255)
        action = serializers.CharField(required=True, max_length=255)
        asset_id = serializers.IntegerField(required=True)
        config_object_type = serializers.CharField(required=True, max_length=255)
        config_object = serializers.CharField(required=True, max_length=255)
        status = serializers.CharField(required=True, max_length=255)
        date = serializers.CharField(required=True, max_length=255)

    items = HistoryItemsSerializer(many=True)
