from rest_framework import serializers

from vmware.serializers.VMware.HostSystem import VMwareHostSystemSerializer


class VMwareDatastoreSerializer(serializers.Serializer):
    assetId = serializers.IntegerField(required=True)
    moId = serializers.CharField(required=True, max_length=255)
    name = serializers.CharField(required=True, max_length=255)
    url = serializers.CharField(required=False, max_length=1024)
    freeSpace = serializers.IntegerField(required=False)
    maxFileSize = serializers.IntegerField(required=False)
    maxVirtualDiskCapacity = serializers.IntegerField(required=False, allow_null=True)
    vmfsType = serializers.CharField(required=False, max_length=64)
    capacity = serializers.IntegerField(required=False)
    majorVersion = serializers.IntegerField(required=False, allow_null=True)
    ssd = serializers.BooleanField(required=False, allow_null=True)
    local = serializers.BooleanField(required=False, allow_null=True)
    multipleHostAccess = serializers.BooleanField(required=False)

    attachedHosts = VMwareHostSystemSerializer(many=True, required=False, allow_null=True)
