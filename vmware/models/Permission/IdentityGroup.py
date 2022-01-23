from typing import List

from vmware.helpers.Utils import GroupConcatToDict

from vmware.repository.IdentityGroup import IdentityGroup as Repository


class IdentityGroup:
    def __init__(self, identityGroupIdentifier: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int
        self.identity_group_identifier = identityGroupIdentifier
        self.name: str



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(self.identity_group_identifier)
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.identity_group_identifier, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.identity_group_identifier)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listWithRelated(showPrivileges: bool = False) -> List[dict]:
        # List identity groups with related information regarding the associated roles on objects
        # and optionally detailed privileges' descriptions.
        j = 0

        try:
            items = Repository.list()

            # "items": [
            # ...,
            # {
            #    "id": 2,
            #    "name": "groupStaff",
            #    "identity_group_identifier": "cn=groupStaff,cn=users,dc=lab,dc=local",
            #    "roles_object": "staff::group-v1082::Varie::1::folder",
            #    "privileges_object": "asset_get::group-v1082::Varie::1::folder,vmware_object_get::group-v1082::Varie::1::folder, ..."
            # },
            # ...
            # ]

            gcR = GroupConcatToDict(["role", "moId", "name", "assetId", "object_type"])
            gcP = GroupConcatToDict(["privilege", "moId", "name", "assetId", "object_type"])

            """
                rStructure data sample:
                 [
                    {
                        "role": "staff", 
                        "moId": "group-v1082",
                        "name": "Varie"
                        "assetId": "1",
                        "object_type": "folder" 
                    }, 
                    {
                        ...
                    }
                ]
            """

            for el in items:
                rStructure = gcR.makeDict(el["roles_object"])
                roleStructure = dict()
                for rs in rStructure:
                    role = rs["role"]
                    if role not in roleStructure:
                        roleStructure[role] = list()

                    roleStructure[role].append(rs)
                el["roles_object"] = roleStructure

                if showPrivileges:
                    pStructure = gcP.makeDict(el["privileges_object"])
                    privStructure = dict()
                    for ps in pStructure:
                        privilege = ps["privilege"]
                        if privilege not in privStructure:
                            privStructure[privilege] = list()

                        privStructure[privilege].append(ps)
                    el["privileges_object"] = privStructure

                else:
                    del items[j]["privileges_object"]

                j = j+1

            return items
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e
