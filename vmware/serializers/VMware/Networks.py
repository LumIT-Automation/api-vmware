from rest_framework import serializers

from vmware.serializers.VMware.Network import VMwareNetworkSerializer


class VMwareNetworksSerializer(serializers.Serializer):
    items = VMwareNetworkSerializer(many=True)
