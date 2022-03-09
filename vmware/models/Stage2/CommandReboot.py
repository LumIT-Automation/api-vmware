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
            privKeyStr = ""

            # Use the key id from the POST payload if passed, get the default private key id from the target otherwise.
            if "priv_key_id" in data and data["priv_key_id"]:
                privKeyStr = data["priv_key_id"]
            else:
                privKeyStr = connectionData["id_bootstrap_key"]
            privKey = BootstrapKey(privKeyStr)
            connectionData["priv_key"] = privKey.priv_key

            # Use the username from the POST payload if passed, get the default username id from the target otherwise.
            if "username" in data and data["username"]:
                connectionData["username"] = data["username"]

            Log.log(data, '_')
            Log.log(connectionData, '_')
            ssh = SshSupplicant(connectionData, silent=silent)
            out = ssh.command("/bin/echo \"Puongiorno\"")

        except Exception as e:
            raise e

        return dict({
            "data": {
                "output": out
            }
        })

