from rest_framework import serializers

class VMwareTaskSerializer(serializers.Serializer):
    entityName = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    entity_moId = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    queueTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    startTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    progress = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    message = serializers.CharField(max_length=64, required=False, allow_blank=True)
