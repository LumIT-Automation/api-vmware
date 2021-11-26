from rest_framework import serializers
from vmware.models.Permission.Privilege import Privilege
from vmware.models.Permission.Role import Role


class IdentityGroupsAssestRolesSubItems(serializers.Serializer):
    moId = serializers.CharField(max_length=64, required=True)
    name = serializers.CharField(max_length=64, required=True)
    assetId = serializers.IntegerField(required=True)

class IdentityGroupsSerializer(serializers.Serializer):
    class IdentityGroupsInnerSerializer(serializers.Serializer):
        class IdentityGroupsAssestItems(serializers.Serializer):
            class IdentityGroupsAssestRolesItems(serializers.Serializer):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

                    # Adding dynamic fields as taken from the Roles model.
                    # Who finds out a better way of doing this, will win a prize, phone me back.
                    additionalFields = []
                    r = Role.list()["items"]
                    for additionalField in r:
                        if "role" in additionalField:
                            additionalFields.append(additionalField["role"])

                    for af in additionalFields:
                        self.fields[af] = IdentityGroupsAssestRolesSubItems(many=True, required=False)

            class IdentityGroupsAssestPrivilegeItems(serializers.Serializer):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

                    # Adding dynamic fields as taken from the Privilege model.
                    additionalFields = []
                    r = Privilege.list()["items"]
                    for additionalField in r:
                        if "privilege" in additionalField:
                            additionalFields.append(additionalField["privilege"])

                    for af in additionalFields:
                        self.fields[af] = IdentityGroupsAssestRolesSubItems(many=True, required=False)

            name = serializers.CharField(max_length=64, required=True)
            identity_group_identifier = serializers.CharField(max_length=255, required=True)

            roles_object = IdentityGroupsAssestRolesItems(required=False)
            privileges_object = IdentityGroupsAssestPrivilegeItems(required=False)

        items = IdentityGroupsAssestItems(many=True)

    data = IdentityGroupsInnerSerializer(required=True)
