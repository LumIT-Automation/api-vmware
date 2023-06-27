from rest_framework import serializers

from vmware.serializers.VMware.Asset.Asset import VMwareAssetSerializer


class VMwareAssetsSerializer(serializers.Serializer):
    items = VMwareAssetSerializer(many=True)
