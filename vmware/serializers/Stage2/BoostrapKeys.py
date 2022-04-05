from rest_framework import serializers

from vmware.serializers.Stage2.BoostrapKey import Stage2BootstrapKeySerializer


class Stage2BootstrapKeysSerializer(serializers.Serializer):
    items = Stage2BootstrapKeySerializer(many=True)
