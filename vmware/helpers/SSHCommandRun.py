import re
import time

from vmware.models.Stage2.Command import Command
from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.BoostrapKey import BootstrapKey
from vmware.models.Stage2.FinalPubKey import FinalPubKey

from vmware.helpers.SSHSupplicant import SSHSupplicant
from vmware.helpers.Exception import CustomException
from vmware.helpers.Log import Log


class SSHCommandRun:
    def __init__(self, commandUid: str, targetId: int, userArgs: dict, *args, **kwargs):
        super().__init__()

        self.targetId = targetId
        self.userArgs = userArgs
        self.pubKeyId = kwargs.get("pubKeyId", 0)
        self.timeout = 10

        try:
            # Load command and its arguments template from db.
            c = Command(commandUid)

            self.commandUid = commandUid
            self.command = c.command
            self.templateArgs = c.args

            # Target connection information.
            self.connectionData = Target(self.targetId).connectionData
            if "id_bootstrap_key" in self.connectionData \
                    and self.connectionData["id_bootstrap_key"]:
                self.connectionData["priv_key"] = BootstrapKey(self.connectionData["id_bootstrap_key"]).priv_key
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, *args, **kwargs) -> str:
        try:
            # Run command (with user arguments) against target (SSH).
            if self.commandUid == "reboot":
                o = self.__reboot()
            elif self.commandUid == "addPubKey":
                o = self.__publicKey()
            else:
                o = self.__command()
        except Exception as e:
            raise e

        return o



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __command(self) -> str:
        try:
            ssh = SSHSupplicant(self.connectionData, tcpTimeout=self.timeout)
            out = ssh.command(
                SSHCommandRun.__commandCompile(
                    self.command, self.userArgs, self.templateArgs
                ).replace("\r", "") # complete and purged command.
            )
        except Exception as e:
            raise e

        return out



    def __publicKey(self) -> str:
        try:
            # Load public key as it was put by the user.
            self.userArgs["__pubKey"] = FinalPubKey(self.pubKeyId).pub_key

            ssh = SSHSupplicant(self.connectionData, tcpTimeout=self.timeout)
            out = ssh.command(
                SSHCommandRun.__commandCompile(
                    self.command, self.userArgs, self.templateArgs, validate=False
                ).replace("\r", "")
            )
        except Exception as e:
            raise e

        return out



    def __reboot(self) -> str:
        o = ""

        try:
            ssh = SSHSupplicant(self.connectionData, tcpTimeout=self.timeout)
            out = ssh.command(
                SSHCommandRun.__commandCompile(
                    self.command, self.userArgs, self.templateArgs).replace("\r", ""),
                alwaysSuccess=True # reboot on RH does not return 0
            )

            # Synchronize reboot command.
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
    def __commandCompile(command: str, userArgs: dict, templateArgs: dict, validate: bool = True) -> str:
        try:
            if validate:
                SSHCommandRun.__validateUserArgs(userArgs, templateArgs) # are args enough and of the correct type?
                userArgs = SSHCommandRun.__cleanupArgs(userArgs) # allow only safe chars.

            # Replace ${argument} in command with userArgs["argument"] value.
            for k, v in userArgs.items():
                command = command.replace("${"+k+"}", v)

            return command
        except Exception as e:
            raise e
