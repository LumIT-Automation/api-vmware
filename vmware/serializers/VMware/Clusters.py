from rest_framework import serializers

from vmware.serializers.VMware.Cluster import VMwareClusterInnerSerializer


class VMwareClustersSerializer(serializers.Serializer):
    class VMwareClustersInnerSerializer(serializers.Serializer):
        items = VMwareClusterInnerSerializer(many=True)

    data = VMwareClustersInnerSerializer(required=True)
