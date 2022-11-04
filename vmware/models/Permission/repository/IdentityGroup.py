from typing import List

from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class IdentityGroup:

    # Table: identity_group`

    #   `id` int(11) NOT NULL,
    #   `name` varchar(64) NOT NULL,
    #   `identity_group_identifier` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int, identityGroupIdentifier: str) -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT * FROM identity_group WHERE id = %s", [id])
            if identityGroupIdentifier:
                c.execute("SELECT * FROM identity_group WHERE identity_group_identifier = %s", [
                    identityGroupIdentifier
                ])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent identity group"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(id: int, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        if IdentityGroup.__exists(id):
            # %s placeholders and values for SET.
            for k, v in data.items():
                sql += k + "=%s,"
                values.append(strip_tags(v)) # no HTML allowed.

            # Condition for WHERE.
            values.append(id)

            try:
                c.execute("UPDATE identity_group SET "+sql[:-1]+" WHERE id = %s",
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": "Non existent identity group"})



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        if IdentityGroup.__exists(id):
            try:
                c.execute("DELETE FROM identity_group WHERE id = %s", [
                    id
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
    def list() -> List[dict]:
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

            Log.log(query, '_')
            c.execute(query)

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []
        c = connection.cursor()

        # Build SQL query according to dict fields (only whitelisted fields pass).
        for k, v in data.items():
            s += "%s,"
            keys += k + ","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO identity_group "+keys+" VALUES ("+s[:-1]+")",
                    values
                )

                return c.lastrowid
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __exists(id: int) -> int:
        c = connection.cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM identity_group WHERE id = %s", [
                id
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
