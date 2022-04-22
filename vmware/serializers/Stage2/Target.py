from rest_framework import serializers


class Stage2TargetSerializer(serializers.Serializer):
    class Stage2TargetSerializerConnection(serializers.Serializer):
        ip = serializers.IPAddressField(required=True)
        port = serializers.IntegerField(required=True)
        api_type = serializers.CharField(required=True, max_length=64)
        id_bootstrap_key = serializers.IntegerField(required=True)
        username = serializers.CharField(required=True, max_length=64)
        password = serializers.CharField(required=False, max_length=64)

    id = serializers.IntegerField(required=False)
    id_asset = serializers.IntegerField(required=False, allow_null=True)
    task_moid = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
    task_state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    task_progress = serializers.IntegerField(required=False, allow_null=True)
    task_startTime = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
    task_queueTime = serializers.CharField(required=False, max_length=64, allow_blank=True, allow_null=True)
    task_message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vm_name = serializers.CharField(required=False, max_length=128, allow_blank=True)
    connection = Stage2TargetSerializerConnection(required=False)

    commands = serializers.JSONField(required=False)
    commandsExecutions = serializers.JSONField(required=False)
