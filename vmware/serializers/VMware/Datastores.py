from rest_framework import serializers

from vmware.serializers.VMware.Datastore import VMwareDatastoreSerializer


class VMwareDatastoresSerializer(serializers.Serializer):
    items = VMwareDatastoreSerializer(many=True)
