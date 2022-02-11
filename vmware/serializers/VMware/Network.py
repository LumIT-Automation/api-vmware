from rest_framework import serializers

from vmware.serializers.VMware.HostSystem import VMwareHostSystemSerializer


class VMwareNetworkSerializer(serializers.Serializer):
    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(max_length=64, required=False)
    name = serializers.CharField(max_length=255, required=False)
    accessible = serializers.BooleanField(required=False)
    type = serializers.CharField(max_length=15, required=False, allow_blank=True)
    vlanId = serializers.CharField(max_length=15, required=False, allow_blank=True)

    configuredHosts = VMwareHostSystemSerializer(many=True, required=False, allow_null=True)
