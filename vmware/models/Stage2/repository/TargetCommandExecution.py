import json
from typing import List

from django.utils.html import strip_tags
from django.db import connections

from vmware.helpers.Exception import CustomException
from vmware.helpers.Database import Database as DBHelper
from vmware.helpers.Log import Log


class TargetCommandExecution:
    db = 'stage2'

    # Table: target_command_exec
    #   `id` int(11) NOT NULL,
    #   `id_target_command` int(11) NOT NULL,
    #   `timestamp` datetime(4) NOT NULL DEFAULT current_timestamp(4),
    #   `exit_status` int(11) NOT NULL,
    #   `stdout` mediumtext NOT NULL DEFAULT '',
    #   `stderr` mediumtext NOT NULL DEFAULT ''



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(targetId: int) -> List[dict]:
        c = connections[TargetCommandExecution.db].cursor()

        try:
            c.execute(
                "SELECT id_target_command, command, exit_status, stdout, stderr, CAST(timestamp AS char) AS timestamp "
                "FROM target_command_exec "
                "LEFT JOIN target_command "
                "ON target_command_exec.id_target_command = target_command.id "
                "WHERE target_command.id_target = %s "
                "ORDER BY target_command.id ASC ", [
                    targetId
            ])
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
        c = connections[TargetCommandExecution.db].cursor()

        # Build SQL query according to dict fields.
        for k, v in data.items():
            s += "%s,"
            keys += k + ","
            values.append(strip_tags(v)) # no HTML allowed.
        keys = keys[:-1]+")"

        try:
            c.execute("INSERT INTO target_command_exec "+keys+" VALUES ("+s[:-1]+")",
                values
            )

            return c.lastrowid
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
