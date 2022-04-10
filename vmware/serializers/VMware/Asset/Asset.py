from rest_framework import serializers


class VMwareAssetSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    address = serializers.IPAddressField(max_length=64, required=True)
    fqdn = serializers.CharField(max_length=255, required=True, allow_blank=True)
    baseurl = serializers.CharField(max_length=255, required=True)
    tlsverify = serializers.IntegerField(required=True)
    datacenter = serializers.CharField(max_length=255, required=True, allow_blank=True)
    environment = serializers.CharField(max_length=255, required=True)
    position = serializers.CharField(max_length=255, required=True, allow_blank=True)
    api_type = serializers.CharField(max_length=64, required=True, allow_blank=True)
    api_additional_data = serializers.CharField(max_length=8192, required=False, allow_blank=True)
    username = serializers.CharField(max_length=64, required=False)
    password = serializers.CharField(max_length=64, required=False)
