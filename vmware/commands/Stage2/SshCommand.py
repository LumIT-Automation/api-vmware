import re

from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.helpers.SshSupplicant import SshSupplicant
from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException

class SshCommand:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.targetId = int(targetId)
        self.shellVars = ""
        self.command = '/bin/echo'
        self.alwaysSuccess = False



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exec(self, data: dict = None, tcpTimeout: int = 10, silent: bool = False) -> dict:
        data = {} if data is None else data
        try:
            target = Target(self.targetId)
            connectionData = target.connectionData
            if connectionData:
                if "id_bootstrap_key" in connectionData and connectionData["id_bootstrap_key"]:
                    privKeyStr = connectionData["id_bootstrap_key"]
                    privKey = BootstrapKey(privKeyStr)
                    connectionData["priv_key"] = privKey.priv_key

                if "sudo" in data and data["sudo"]:
                    command = '[ `id -u` -eq 0 ] || sudo -i; set -e;'+self.command
                else:
                    command = 'set -e;'+self.command

                # Pass the value of the variables to the shell script.
                # Example: scriptVar={httpPutVar}. The value of {httpPutVar} ends in $scriptVar.
                if self.shellVars and "shellVars" in data:
                    dataShellVars = self.cleanupShellParams(data["shellVars"])
                    self.shellVars = self.shellVars.format(**dataShellVars) # Variables substitution.
                    command = self.shellVars + command

                ssh = SshSupplicant(connectionData, tcpTimeout=tcpTimeout, silent=silent)
                out = ssh.command(command, alwaysSuccess=self.alwaysSuccess)
            else:
                raise CustomException(status=400, payload={"Ssh": "Target not found."})

        except Exception as e:
            raise e

        return dict({
            "data": {
                "output": out
            }
        })



    def cleanupShellParams(self, shellVars: dict):
        try:
            def cleanString(inputString: str):
                return re.sub(r'[^a-z0-9A-Z_/-]+', '', inputString, 0)

            for key, value in shellVars.items():
                Log.log(str(key) + " " + str(value), '_')
                if isinstance(value, str):
                    shellVars[key] = cleanString(value)
                elif isinstance(value, int):
                    pass
                else:
                    raise CustomException(status=400, payload={"Ssh": "Forbidden data type in shellVars"})

            return shellVars
        except Exception as e:
            raise e
