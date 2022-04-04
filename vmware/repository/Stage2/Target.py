from typing import List

from django.utils.html import strip_tags
from django.db import connections
from django.db import transaction

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class Target:
    db = 'stage2'

    # Table: stage2_target
    #   `id` int(11) NOT NULL,
    #   `ip` varchar(64) NOT NULL,
    #   `port` int(11) DEFAULT NULL,
    #   `api_type` varchar(64) NOT NULL DEFAULT '',
    #   `id_bootstrap_key` int(11) DEFAULT NULL,
    #   `username` varchar(64) NOT NULL DEFAULT '',
    #   `password` varchar(64) NOT NULL DEFAULT ''
    #   `id_asset` int(11) NOT NULL,
    #   `task_moid` varchar(63) NOT NULL DEFAULT '',
    #   `task_state` varchar(63) NOT NULL DEFAULT 'undefined',
    #   `task_progress` int(11) DEFAULT NULL,
    #   `task_startTime` varchar(64) NOT NULL DEFAULT '',
    #   `task_queueTime` varchar(64) NOT NULL DEFAULT '',
    #   `vm_name` varchar(127) NOT NULL DEFAULT '';



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(targetId: int) -> dict:
        c = connections[Target.db].cursor()
        o = dict()

        try:
            c.execute("SELECT * FROM target "
                      "WHERE target.id = %s ", [
                        targetId
                    ])

            a = DBHelper.asDict(c)[0]
            if a["api_type"] == "ssh":
                o["connectionData"] = {
                    "ip": a["ip"],
                    "port": a["port"],
                    "api_type": a["api_type"],
                    "id_bootstrap_key": a["id_bootstrap_key"],
                    "username": a["username"],
                    "password": a["password"]
                }
                o["id"] = a["id"]
                o["id_asset"] = a["id_asset"]
                o["task_moid"] = a["task_moid"]
                o["task_state"] = a["task_state"]
                o["task_progress"] = a["task_progress"]
                o["task_startTime"] = a["task_startTime"]
                o["task_queueTime"] = a["task_queueTime"]
                o["vm_name"] = a["vm_name"]

                return o
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def getInfo(targetId: int) -> dict:
        c = connections[Target.db].cursor()

        try:
            c.execute(
                "SELECT "
                    "target.id, target.ip, target.port, "
                    "target.api_type, target.id_bootstrap_key, target.username, "
                    "target.id_asset, target.task_moid, target.task_state, target.task_progress, "
                    "target.task_startTime, target.task_queueTime, "
                    "target.vm_name, target.id, "
                    "GROUP_CONCAT("
                        "CONCAT(final_pubkey.id,'::',final_pubkey.comment,'::',final_pubkey.pub_key) "
                    ")  AS final_pubkeys "
                "FROM target "
                "LEFT JOIN target_final_pubkey ON target_final_pubkey.id_target = target.id "
                "LEFT JOIN final_pubkey on final_pubkey.id = target_final_pubkey.id_pubkey "
                "WHERE target.id = %s ", [
                    targetId
                ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(targetId: int, data: dict) -> None:
        sql = ""
        values = []
        c = connections[Target.db].cursor()

        if Target.__exists(targetId):
            # Build the update query according to dict fields.
            for k, v in data.items():
                if v is None:
                    sql += k+"=DEFAULT,"
                else:
                    sql += k+"=%s,"
                    values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute(
                    "UPDATE target SET "+sql[:-1]+" WHERE id = "+str(targetId),
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def delete(targetId: int) -> None:
        c = connections[Target.db].cursor()

        if Target.__exists(targetId):
            try:
                c.execute("DELETE FROM target WHERE id = %s", [
                    targetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()
        else:
            raise CustomException(status=404, payload={"database": "Non existent endpoint"})



    @staticmethod
    def list() -> List[dict]:
        c = connections[Target.db].cursor()

        try:
            c.execute(
                "SELECT "
                "id, ip, port, api_type, id_bootstrap_key, id_asset, "
                "task_moid, task_state,task_progress, task_startTime, task_queueTime, vm_name "
                "FROM target"
            )
            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []
        pubKeysIds = []
        pubKeysPlaceholders = ""
        c = connections[Target.db].cursor()

        # Build the last part of the insert query.
        if "final_pubkeys" in data:
            if data["final_pubkeys"]:
                for el in data["final_pubkeys"]:
                    pubKeysPlaceholders += "(%s, %s),"
                    pubKeysIds.extend([0, el["id"]]) # zero is for the targetId which does not exist yet.
            del data["final_pubkeys"]

        # Build SQL query according to dict fields.
        for k, v in data.items():
            s += "%s,"
            keys += k+","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO target "+keys+" VALUES ("+s[:-1]+")",
                    values
                )
                targetId = c.lastrowid

                # Replace zeroes (which have the even indexes in the list) with the created targetId.
                for i in range(0, len(pubKeysIds), 2):
                    pubKeysIds[i] = targetId

                if pubKeysIds:
                    c.execute(
                        "INSERT INTO target_final_pubkey (`id_target`, `id_pubkey`) VALUES "+pubKeysPlaceholders[:-1],
                            pubKeysIds
                    )

                return targetId
        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __exists(targetId: int) -> int:
        c = connections[Target.db].cursor()

        try:
            c.execute("SELECT COUNT(*) AS c FROM target WHERE id = %s", [
                targetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
