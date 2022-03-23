from rest_framework import serializers


class Stage2TargetsSerializer(serializers.Serializer):
    class Stage2TargetsInnerSerializer(serializers.Serializer):
        class Stage2TargetsItems(serializers.Serializer):
            id = serializers.IntegerField(required=True)
            ip = serializers.IPAddressField(required=True)
            port = serializers.IntegerField(required=True)
            api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)
            id_bootstrap_key = serializers.IntegerField(required=False, allow_null=True)
            id_asset = serializers.IntegerField(required=False, allow_null=True)
            task_moid = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True)
            task_status = serializers.CharField(max_length=64, required=False)
            vm_name = serializers.CharField(max_length=128, required=False, allow_blank=True)

        items = Stage2TargetsItems(many=True)

    data = Stage2TargetsInnerSerializer(required=True)
