
from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.helpers.SshSupplicant import SshSupplicant
from vmware.helpers.Log import Log

class SshCommand:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.targetId = int(targetId)
        self.command = '/bin/echo'

    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exec(self, data: dict,  silent: bool = False) -> dict:
        out = ""
        try:
            target = Target(self.targetId)
            connectionData = target.connectionData

            if "id_bootstrap_key" in connectionData and connectionData["id_bootstrap_key"]:
                privKeyStr = connectionData["id_bootstrap_key"]
                privKey = BootstrapKey(privKeyStr)
                connectionData["priv_key"] = privKey.priv_key

            sudoCommand='[ `id -u` -eq 0 ] || SUDO="sudo";$SUDO '+self.command
            ssh = SshSupplicant(connectionData, silent=silent)
            out = ssh.command(sudoCommand)

        except Exception as e:
            raise e

        return dict({
            "data": {
                "output": out
            }
        })

