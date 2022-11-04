from typing import List, Dict

from django.db import connection

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Utils import GroupConcatToDict


class PermissionPrivilege:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(showPrivileges: bool = False) -> list:
        # List identity groups with related information regarding the associated roles on objects,
        # and optionally detailed privileges' descriptions.
        j = 0
        c = connection.cursor()

        try:
            query = (
                "SELECT "
                    "identity_group.*, "
    
                    "IFNULL( "
                        "GROUP_CONCAT( "
                            "DISTINCT CONCAT( "
                            "role.role,'::',CONCAT( "
                                "vmware_object.moId,'::',vmware_object.name,'::',vmware_object.id_asset,'::', "
                                    "(CASE SUBSTRING_INDEX(vmware_object.moId, '-', 1) "
                                    "WHEN 'any' THEN 'any' "
                                    "WHEN 'group' THEN 'folder' "
                                    "WHEN 'datastore' THEN 'datastore' "
                                    "WHEN 'network' THEN 'network' "
                                    "WHEN 'dvportgroup' THEN 'network' "
                                    "END) "
                                    ") "
                                ") "
                            "ORDER BY role.id SEPARATOR ',' "
                        "), '' "
                    ") AS roles_object, "
    
                    "IFNULL( "
                        "GROUP_CONCAT( "
                            "DISTINCT( "
                                "CASE SUBSTRING_INDEX(privilege.privilege_type, '-', 1) "
                                    "WHEN 'global' THEN CONCAT(privilege.privilege,'::any::any::0::global') "
                                    "WHEN 'asset' THEN CONCAT(privilege.privilege,'::any::any::',vmware_object.id_asset,'::asset') "
                                    "WHEN 'object' THEN "
                                    "IF( "
                                        "SUBSTRING_INDEX(vmware_object.moId, '-', 1) = SUBSTRING_INDEX(privilege.privilege_type, '-', -1), "
                                        "CONCAT( "
                                        "privilege.privilege,'::',vmware_object.moId,'::',vmware_object.name,'::',vmware_object.id_asset,'::', "
                                            "(CASE SUBSTRING_INDEX(vmware_object.moId, '-', 1) "
                                                "WHEN 'group' THEN 'folder' "
                                                "WHEN 'datastore' THEN 'datastore' "
                                                "WHEN 'network' THEN 'network' "
                                                "WHEN 'dvportgroup' THEN 'network' "
                                            "END) "
                                        "), "
                                        "NULL "
                                    ") "
                                "END "
                            ") "
                            "ORDER BY privilege.id SEPARATOR ',' "
                        "), "
                        "'' "
                    ") AS privileges_object "

                "FROM identity_group "
                "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_object.id_role "
                "LEFT JOIN `vmware_object` ON `vmware_object`.id = group_role_object.id_object "
                "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                "GROUP BY identity_group.id "
            )

            c.execute(query)
            items: List[Dict] = DBHelper.asDict(c)

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
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
