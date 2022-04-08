import re
import time

from vmware.models.Stage2.Command import Command
from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey

from vmware.helpers.SSHSupplicant import SSHSupplicant
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class SSHCommandRun:
    def __init__(self, commandUid: str, targetId: int, userArgs: dict, silent: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            # Load command and its arguments template from db.
            c = Command(commandUid)

            self.commandUid = commandUid
            self.command = c.command
            self.templateArgs = c.args
        except Exception as e:
            raise e

        self.targetId = targetId
        self.userArgs = userArgs

        self.alwaysSuccess = False
        self.timeout = 10
        self.silent = silent



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, *args, **kwargs) -> str:
        try:
            # Target connection information.
            connectionData = Target(self.targetId).connectionData
            if "id_bootstrap_key" in connectionData and connectionData["id_bootstrap_key"]:
                connectionData["priv_key"] = BootstrapKey(connectionData["id_bootstrap_key"]).priv_key

            if self.commandUid == "reboot":
                self.alwaysSuccess = True # reboot on RH does not return 0.

            # Run command (with user arguments) against target (SSH).
            ssh = SSHSupplicant(connectionData, tcpTimeout=self.timeout, silent=self.silent)
            out = ssh.command(
                SSHCommandRun.__commandCompile(self.command, self.userArgs, self.templateArgs).replace("\r", ""), # complete and purged command.
                alwaysSuccess=self.alwaysSuccess
            )

            # Synchronize reboot command.
            if self.commandUid == "reboot":
                o = ""
                tStart = time.time()
                while time.time() < tStart + 120: # [seconds]
                    try:
                        o = SSHCommandRun("echo", self.targetId, {"__echo": "i-am-alive"})()
                        if o:
                            break
                    except Exception:
                        pass

                    time.sleep(10) # every 10s.

                if not o:
                    raise CustomException(status=400, payload={"Ssh": "machine not responding anymore."})
        except Exception as e:
            raise e

        return out



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __validateUserArgs(userArgs: dict, templateArgs: dict):
        # Validate user args against args template.

        try:
            # User args must be of the expected type (i.e. the type specified in the template args).
            for ku, vu in userArgs.items():
                if isinstance(vu, eval(templateArgs[ku])):
                    del(templateArgs[ku]) # delete to keep track of available args.
                else:
                    raise CustomException(status=400, payload={"Ssh": "forbidden data type in args."})

            # All template args passed?
            if templateArgs:
                raise CustomException(status=400, payload={"Ssh": "some args missing."})
        except KeyError:
            # Something not needed passed (causing a KeyError).
            raise CustomException(status=400, payload={"Ssh": "some args not required."})



    @staticmethod
    def __cleanupArgs(args: dict) -> dict:
        try:
            def cleanString(inputString: str):
                return re.sub(r'[^a-z0-9A-Z_/-]+', '', inputString, 0)

            # Allow ony safe chars in args.
            for key, value in args.items():
                if isinstance(value, str):
                    args[key] = cleanString(value)

            return args
        except Exception as e:
            raise e



    @staticmethod
    def __commandCompile(command: str, userArgs: dict, templateArgs: dict) -> str:
        try:
            # Are args enough and of the correct type?
            SSHCommandRun.__validateUserArgs(userArgs, templateArgs)

            # Replace ${argument} in command with userArgs["argument"] value.
            for k, v in SSHCommandRun.__cleanupArgs(userArgs).items():
                command = command.replace("${"+k+"}", v)

            return command
        except Exception as e:
            raise e
