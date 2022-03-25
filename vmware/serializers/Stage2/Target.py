from rest_framework import serializers

from vmware.serializers.Stage2.FinalPubKey import Stage2FinalPubKeySerializer


class Stage2TargetSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    ip = serializers.IPAddressField(required=False)
    port = serializers.IntegerField(required=False)
    api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)
    id_bootstrap_key = serializers.IntegerField(required=False, allow_null=True)
    username = serializers.CharField(max_length=64, required=False, allow_blank=True)
    password = serializers.CharField(max_length=64, required=False, allow_blank=True)
    id_asset = serializers.IntegerField(required=False, allow_null=True)

    task_moid = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    task_state = serializers.CharField(max_length=64, required=False)
    task_progress = serializers.IntegerField(required=False, allow_null=True)
    task_startTime = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    task_queueTime = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
    vm_name = serializers.CharField(max_length=128, required=False, allow_blank=True)

    final_pubkeys = Stage2FinalPubKeySerializer(many=True, required=False, allow_null=True)