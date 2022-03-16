import re

from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.helpers.SshSupplicant import SshSupplicant
from vmware.helpers.Log import Log

class SshCommand:
    def __init__(self, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.targetId = int(targetId)
        self.shellVars = ""
        self.command = '/bin/echo'



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exec(self, data: dict = None, silent: bool = False) -> dict:
        data = {} if data is None else data
        out = ""
        try:
            target = Target(self.targetId)
            connectionData = target.connectionData
            Log.log(connectionData, '_')

            if "id_bootstrap_key" in connectionData and connectionData["id_bootstrap_key"]:
                privKeyStr = connectionData["id_bootstrap_key"]
                privKey = BootstrapKey(privKeyStr)
                connectionData["priv_key"] = privKey.priv_key

            if "sudo" in data and data["sudo"]:
                command = '[ `id -u` -eq 0 ] || sudo -i;'+self.command
            else:
                command = self.command

            # Pass the value of the variables to the shell script.
            # Example: scriptVar={httpPutVar}. The value of {httpPutVar} ends in $scriptVar.
            if self.shellVars and "shellVars" in data:
                dataShellVars = self.cleanupShellParams(data["shellVars"])
                self.shellVars = self.shellVars.format(**dataShellVars) # Variables substitution.
                command = self.shellVars + command

            Log.log('Trying ssh command: ' + str(command))
            ssh = SshSupplicant(connectionData, silent=silent)
            out = ssh.command(command)

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

            return shellVars
        except Exception as e:
            raise e
