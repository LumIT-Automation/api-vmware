from rest_framework import serializers

from vmware.serializers.VMware.Cluster import VMwareClusterSerializer


class VMwareClustersSerializer(serializers.Serializer):
    items = VMwareClusterSerializer(many=True)
