from rest_framework import serializers

class VMwareTaskSerializer(serializers.Serializer):
    entityName = serializers.CharField(required=True, max_length=255)
    entity_moId = serializers.CharField(required=True, max_length=64)
    queueTime = serializers.DateTimeField(required=True, format="%Y-%m-%d %H:%M:%S")
    startTime = serializers.DateTimeField(required=True, format="%Y-%m-%d %H:%M:%S")
    progress = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.CharField(required=True, max_length=64)
    message = serializers.CharField(required=False, max_length=64, allow_blank=True)
