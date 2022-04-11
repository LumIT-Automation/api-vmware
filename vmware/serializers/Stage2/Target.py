from rest_framework import serializers

from vmware.serializers.Stage2.Command import Stage2CommandSerializer


class Stage2TargetSerializer(serializers.Serializer):
    class Stage2TargetSerializerConnection(serializers.Serializer):
        ip = serializers.IPAddressField(required=False)
        port = serializers.IntegerField(required=False)
        api_type = serializers.CharField(required=True, max_length=64, allow_blank=True)
        id_bootstrap_key = serializers.IntegerField(required=False, allow_null=True)
        username = serializers.CharField(required=False, max_length=64, allow_blank=True)
        password = serializers.CharField(required=False, max_length=64, allow_blank=True)

    id = serializers.IntegerField(required=False)
    id_asset = serializers.IntegerField(required=False, allow_null=True)
    task_moid = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
    task_progress = serializers.IntegerField(required=False, allow_null=True)
    task_startTime = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
    task_queueTime = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
    vm_name = serializers.CharField(required=False, max_length=128, allow_blank=True)
    connection = Stage2TargetSerializerConnection(required=False)

    commands = Stage2CommandSerializer(many=True, required=False)
