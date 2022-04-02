from rest_framework import serializers

from vmware.serializers.VMware.HostSystem import VMwareHostSystemSerializer


class VMwareNetworkSerializer(serializers.Serializer):
    assetId = serializers.IntegerField()
    moId = serializers.CharField(required=True, max_length=64)
    name = serializers.CharField(required=True, max_length=255)
    accessible = serializers.BooleanField(required=False)
    type = serializers.CharField(required=False, max_length=15, allow_blank=True)
    vlanId = serializers.CharField(required=False, max_length=15, allow_blank=True)

    configuredHosts = VMwareHostSystemSerializer(many=True, required=False, allow_null=True)
