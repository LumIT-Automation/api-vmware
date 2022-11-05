from typing import List, Dict

from django.db import connection

from vmware.models.VMware.FolderVM import FolderVM

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



    @staticmethod
    def countUserPermissions(groups: list, action: str, objectType: str, assetId: int = 0, objectMoId: str = "") -> int:
        if action and groups:
            args = groups.copy()
            assetWhere = ""
            objectWhere = ""

            c = connection.cursor()

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for _ in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND vmware_object.id_asset = %s "

                if objectMoId:
                    objectWhere = "AND ( vmware_object.moId = 'any' "  # if "any" appears in the query results so far -> pass.
                    if objectType == "folder":
                        f = FolderVM(assetId, objectMoId)
                        foldersMoIdsList = f.parentList()
                        foldersMoIdsList.append(objectMoId)
                        objectWhere += "OR ("
                        for moId in foldersMoIdsList:
                            args.append(moId)
                            objectWhere += "vmware_object.moId = %s OR "
                        objectWhere = objectWhere[:-3] + ") "
                    elif objectType == "datastore":
                        objectWhere += "OR (vmware_object.moId = %s) "
                        args.append(objectMoId)
                    elif objectType == "network":
                        objectWhere += "OR (vmware_object.moId = %s) "
                        args.append(objectMoId)
                    else:
                        raise CustomException(status=400, payload={
                            "database": "\"object_type\" can have only one of these values: folder,datastore,network"})
                    objectWhere += ") "

                args.append(action)

                query = (
                    "SELECT COUNT(*) AS count "
                    "FROM identity_group "
                    "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                    "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                    "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                    "LEFT JOIN vmware_object ON vmware_object.id = group_role_object.id_object "

                    "WHERE (" + groupWhere[:-4] + ") " +
                    assetWhere +
                    objectWhere +
                    "AND privilege.privilege = %s "
                )

                c.execute(query, args)
                return DBHelper.asDict(c)[0]["count"]
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return False



    @staticmethod
    def allowedObjectsByPrivilegeSet(groups: list, action: str, assetId: int = 0) -> set:
        if action and groups:
            args = groups.copy()
            groupWhere = ""
            assetWhere = ""

            c = connection.cursor()

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)

                for _ in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND vmware_object.id_asset = %s "

                args.append(action)

                query = (
                    "SELECT vmware_object.moId "
                    "FROM identity_group "
                    "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                    "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                    "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                    "LEFT JOIN vmware_object ON vmware_object.id = group_role_object.id_object "
                    
                    "WHERE (" + groupWhere[:-4] + ") " +
                    assetWhere +
                    "AND "
                    "(vmware_object.moId = 'any' OR "
                    "CASE SUBSTRING_INDEX(privilege.privilege_type, '-', -1) "
                    "WHEN 'network' THEN ((SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'network') || (SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'dvportgroup')) "
                    "WHEN 'datastore' THEN (SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'datastore') "
                    "WHEN 'folder' THEN (SUBSTRING_INDEX(vmware_object.moId, '-', 1) = 'group') "
                    "END "
                    ") "
                    "AND privilege.privilege = %s "
                )

                c.execute(query, args)
                return DBHelper.columnAsSet(c)
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
