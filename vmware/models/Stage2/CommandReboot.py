import json

from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.helpers.SshSupplicant import SshSupplicant
from vmware.helpers.Log import Log

class CommandReboot:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.targetId = int(targetId)


    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exec(self, data: dict,  silent: bool = False) -> dict:
        out = ""
        try:
            target = Target(self.targetId)
            connectionData = target.connectionData

            if "priv_key_id" in data and data["priv_key_id"]:
                privKey = BootstrapKey(keyId=data["priv_key_id"])
                connectionData["priv_key"] = privKey.priv_key
                Log.log(connectionData, 'KKKKKKKKKKKKKKKK')

            ssh = SshSupplicant(connectionData, silent=silent)
            out = ssh.command("/bin/echo \"Ribbutto\" > /tmp/ciccio.txt")

        except Exception as e:
            raise e

        return dict({
            "data": {
                "output": out
            }
        })

