from rest_framework import serializers


class VMwareAssetSerializer(serializers.Serializer):
    class VMwareAssetInnerSerializer(serializers.Serializer):
        address = serializers.CharField(max_length=64, required=True) # @todo: only valid data.
        fqdn = serializers.CharField(max_length=255, required=True, allow_blank=True) # @todo: only valid data.
        baseurl = serializers.CharField(max_length=255, required=True) # @todo: only valid data.
        tlsverify = serializers.IntegerField(required=True)
        datacenter = serializers.CharField(max_length=255, required=True, allow_blank=True)
        environment = serializers.CharField(max_length=255, required=True)
        position = serializers.CharField(max_length=255, required=True, allow_blank=True)
        api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)
        api_additional_data = serializers.CharField(max_length=8192, required=False, allow_blank=True)
        username = serializers.CharField(max_length=64, required=True)
        password = serializers.CharField(max_length=64, required=True)

    data = VMwareAssetInnerSerializer(required=True)
