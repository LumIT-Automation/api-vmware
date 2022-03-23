from rest_framework import serializers


class Stage2TargetSerializer(serializers.Serializer):
    class Stage2TargetInnerSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        ip = serializers.IPAddressField(required=True)
        port = serializers.IntegerField(required=True)
        api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)
        id_bootstrap_key = serializers.IntegerField(required=False, allow_null=True)
        username = serializers.CharField(max_length=64, required=False, allow_blank=True)
        password = serializers.CharField(max_length=64, required=False, allow_blank=True)
        id_asset = serializers.IntegerField(required=False, allow_null=True)
        task_moid = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        task_status = serializers.CharField(max_length=64, required=False)
        task_progress = serializers.IntegerField(required=False, allow_null=True)
        task_startTime = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        task_queueTime = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
        vm_name = serializers.CharField(max_length=128, required=False, allow_blank=True)

    data = Stage2TargetInnerSerializer(required=True)
