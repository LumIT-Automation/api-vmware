from rest_framework import serializers


class IdentityRolesSerializer(serializers.Serializer):
    class IdentityRolesInnerSerializer(serializers.Serializer):
        class IdentityRolesItemsSerializer(serializers.Serializer):
            role = serializers.CharField(max_length=63, required=True)
            description = serializers.CharField(max_length=255, required=True)
            privileges = serializers.ListField(
                child=serializers.CharField(max_length=63), required=False
            )

        items = IdentityRolesItemsSerializer(many=True)

    data = IdentityRolesInnerSerializer(required=True)
