from django.db import connection
from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Utils import GroupConcatToDict



class Authorization:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groups: list) -> dict:
        permissions = dict()
        c = connection.cursor()


        try:
            if groups:
                # Build the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for g in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                query = ("SELECT "
                        "privilege.privilege, "
                        "IFNULL( "
                            "GROUP_CONCAT( "
                                "DISTINCT CONCAT(vmObject.id_asset,'::',vmObject.moId,'::',vmObject.name,'::',"
                                    "(CASE SUBSTRING_INDEX(vmObject.moId, '-', 1) "
                                        "WHEN 'group' THEN 'folder' "
                                        "WHEN 'datastore' THEN 'datastore' "
                                        "WHEN 'network' THEN 'network' "
                                        "WHEN 'dvportgroup' THEN 'network' "
                                    "END)) "
                                "ORDER BY vmObject.moId SEPARATOR ',' "
                            "), ''"
                        ") AS privilege_objects "                  
                        "FROM identity_group "
                        "LEFT JOIN group_role_object ON group_role_object.id_group = identity_group.id "
                        "LEFT JOIN role_privilege ON role_privilege.id_role = group_role_object.id_role "
                        "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                        "LEFT JOIN vmObject ON vmObject.id = group_role_object.id_object "
                        "WHERE ("+groupWhere[:-4]+") " +
                        "GROUP BY privilege.privilege "

                )

                c.execute(query, groups)
                items = DBHelper.asDict(c)

                aIn = GroupConcatToDict(["assetId", "moId", "objectName", "object_type"])

                for el in items:
                    if el["privilege_objects"]:
                        pStructure = aIn.makeDict(el["privilege_objects"])
                        permissions.update({ el["privilege"]: pStructure })

            return {
                "items": permissions
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()

