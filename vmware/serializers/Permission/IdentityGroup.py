from rest_framework import serializers
from vmware.models.Permission.Role import Role


class IdentityGroupsAssestRolesSubItems(serializers.Serializer):
    moId = serializers.CharField(max_length=63, required=True)
    name = serializers.CharField(max_length=63, required=True)
    assetId = serializers.IntegerField(required=True)
    object_type = serializers.CharField(max_length=63, required=True)

class IdentityGroupsAssestRolesItems(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding dynamic fields as taken from the Roles model.
        additionalFields = []
        r = Role.list()
        for additionalField in r:
            if "role" in additionalField:
                additionalFields.append(additionalField["role"])

        for af in additionalFields:
            self.fields[af] = IdentityGroupsAssestRolesSubItems(many=True, required=False)

class IdentityGroupSerializer(serializers.Serializer):
    class IdentityGroupAssestItems(serializers.Serializer):
        name = serializers.CharField(max_length=63, required=True)
        identity_group_identifier = serializers.CharField(max_length=255, required=True)
        roles_object = IdentityGroupsAssestRolesItems(required=False)

    data = IdentityGroupAssestItems(required=True)
