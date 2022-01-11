from django.utils.html import strip_tags
from django.db import transaction

from vmware.models.Permission.Permission import Permission

from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Utils import GroupConcatToDict

from django.db import connection



class IdentityGroup:
    def __init__(self, identityGroupIdentifier: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.identityGroupIdentifier = identityGroupIdentifier



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM identity_group WHERE identity_group_identifier = %s", [
                self.identityGroupIdentifier
            ])

            return DBHelper.asDict(c)[0]

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def modify(self, data: dict) -> None:
        sql = ""
        values = []
        roles = dict()

        c = connection.cursor()
        if self.__exists():
            for k, v in data.items():
                if any(exc in k for exc in (
                        "roles_object",
                )):
                    # "roles_object": {
                    #     "staff": [
                    #       {
                    #           "moId": "group-v2476",
                    #           "name": "riurca",
                    #           "assetId": 1
                    #       }
                    #     ],
                    #  "nonExistent": []
                    # }

                    if isinstance(v, dict):
                        for rk, rv in v.items():
                            roles[rk] = rv
                else:
                    sql += k + "=%s,"
                    values.append(strip_tags(v))  # no HTML allowed.

            try:
                with transaction.atomic():
                    identityGroupId = self.info()["id"]

                    # Patch identity group.
                    c.execute("UPDATE identity_group SET "+sql[:-1]+" WHERE id = "+str(identityGroupId),
                        values
                    )

                    # Replace associated roles with roles[]' elements.
                    try:
                        # Empty existent roles.
                        Permission.cleanup(identityGroupId)
                    except Exception:
                        pass

                    # Add associated roles (no error on non-existent role).
                    for roleName, objectsList in roles.items():
                        for objectDict in objectsList:
                            try:
                                Permission.add(identityGroupId, roleName, objectDict["assetId"], objectDict["moId"], objectDict["name"])
                            except Exception:
                                pass

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": "Non existent identity group"})



    def delete(self) -> None:
        c = connection.cursor()

        if self.__exists():
            try:
                c.execute("DELETE FROM identity_group WHERE identity_group_identifier = %s", [
                    self.identityGroupIdentifier
                ])

                # Foreign keys' on cascade rules will clean the linked items on db.

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": "Non existent identity group"})



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(showPrivileges: bool = False) -> dict:
        # List identity groups with related information regarding the associated roles on objects
        # and optionally detailed privileges' descriptions.

        j = 0
        c = connection.cursor()

        try:
            c.execute("SELECT "
                "identity_group.*, " 

                "IFNULL(GROUP_CONCAT( "
                    "DISTINCT CONCAT(role.role,'::',CONCAT(vmObject.moId,'::',vmObject.name,'::',vmObject.id_asset,'::',vmObject.object_type)) " 
                    "ORDER BY role.id "
                    "SEPARATOR ',' "
                "), '') AS roles_object, "

                "IFNULL(GROUP_CONCAT( "
                    "DISTINCT CONCAT(privilege.privilege,'::',vmObject.moId,'::',vmObject.name,'::',vmObject.id_asset,'::',vmObject.object_type) " 
                    "ORDER BY privilege.id "
                    "SEPARATOR ',' "
                "), '') AS privileges_object "

                "FROM identity_group "
                "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_object.id_role "
                "LEFT JOIN `vmObject` ON `vmObject`.moId = group_role_object.id_object "
                "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                "GROUP BY identity_group.id"
            )

            items = DBHelper.asDict(c)

            # "items": [
            # ...,
            # {
            #    "id": 2,
            #    "name": "groupStaff",
            #    "identity_group_identifier": "cn=groupStaff,cn=users,dc=lab,dc=local",
            #    "roles_object": "staff::group-v1082::Varie::1::folder",
            #    "privileges_object": "asset_get::group-v1082::Varie::1::folder,vmObject_get::group-v1082::Varie::1::folder, ..."
            # },
            # ...
            # ]

            gcR = GroupConcatToDict(["role", "moId", "name", "assetId","object_type"])
            gcP = GroupConcatToDict(["privilege", "moId", "name","assetId","object_type"])
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
                    if not role in roleStructure:
                        roleStructure[role] = list()

                    roleStructure[role].append(rs)
                el["roles_object"] = roleStructure


                if showPrivileges:
                    pStructure = gcP.makeDict(el["privileges_object"])
                    privStructure = dict()
                    for ps in pStructure:
                        privilege = ps["privilege"]
                        if not privilege in privStructure:
                            privStructure[privilege] = list()

                        privStructure[privilege].append(ps)
                    el["privileges_object"] = privStructure

                else:
                    del items[j]["privileges_object"]

                j = j+1

            return dict({
                "items": items
            })

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> None:
        s = ""
        keys = "("
        values = []
        roles = dict()

        c = connection.cursor()

        # Build SQL query according to dict fields (only whitelisted fields pass).
        for k, v in data.items():
            # roles_object is a dictionary of related roles/objects, which is POSTed together with the main identity group item.
            if any(exc in k for exc in (
                    "roles_object",
            )):
                # "roles_object": {
                #     "staff": [
                #       {
                #           "moId": "group-v2476",
                #           "name": "riurca",
                #           "assetId": 1
                #       }
                #     ],
                #  "nonExistent": []
                # }

                if isinstance(v, dict):
                    for rk, rv in v.items():
                        roles[rk] = rv
            else:
                s += "%s,"
                keys += k + ","
                values.append(strip_tags(v))  # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                # Insert identity group.
                c.execute("INSERT INTO identity_group "+keys+" VALUES ("+s[:-1]+")",
                    values
                )
                igId = c.lastrowid

                # Add associated roles (no error on non-existent role).
                for roleName, objectsList in roles.items():
                    for objectDict in objectsList:
                        try:
                            Permission.add(igId, roleName, objectDict["assetId"], objectDict["moId"], objectDict["name"])
                        except Exception:
                            pass

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __exists(self) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM identity_group WHERE identity_group_identifier = %s", [
                self.identityGroupIdentifier
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])

        except Exception:
            return 0
        finally:
            c.close()
