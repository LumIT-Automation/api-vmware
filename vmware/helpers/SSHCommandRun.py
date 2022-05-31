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
        self.timeout = 10

        try:
            # Load command and its arguments template from db.
            c = Command(commandUid)

            self.commandUid = commandUid
            self.command = c.command
            self.templateArgs = c.template_args

            # Target connection information.
            self.connection = Target(self.targetId).connection
            if "id_bootstrap_key" in self.connection \
                    and self.connection["id_bootstrap_key"]:
                self.connection["priv_key"] = BootstrapKey(self.connection["id_bootstrap_key"]).priv_key
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, *args, **kwargs) -> tuple:
        try:
            # Run command (with user arguments) against target (SSH).
            if self.commandUid == "reboot":
                o, e, s = self.__reboot()
            elif self.commandUid == "waitPowerOn":
                o, e, s = self.__waitPowerOn()
            elif self.commandUid == "addPubKey" \
                    or self.commandUid == "removeBootstrapKey":
                o, e, s = self.__publicKey()
            else:
                o, e, s = self.__command()

            return o, e, s
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __command(self) -> tuple:
        try:
            ssh = SSHSupplicant(self.connection, tcpTimeout=self.timeout)
            out, err, status = ssh.command(
                SSHCommandRun.__commandCompile(
                    self.command, self.userArgs, self.templateArgs
                ) # complete and purged command.
            )

            return out, err, status
        except Exception as e:
            raise e



    def __publicKey(self) -> tuple:
        out = err = ""
        status = -1

        if self.commandUid in ("addPubKey", "removeBootstrapKey"):
            try:
                if self.commandUid == "addPubKey":
                    # Load public key as it was put by the user.
                    self.userArgs["__pubKey"] = FinalPubKey(self.userArgs["__pubKeyId"]).pub_key
                else:
                    # Load public bootstrap key.
                    target = Target(self.targetId)
                    self.userArgs["__pubKey"] = target.getBootstrapPubKey()

                ssh = SSHSupplicant(self.connection, tcpTimeout=self.timeout)
                out, err, status = ssh.command(
                    SSHCommandRun.__commandCompile(
                        self.command, self.userArgs, self.templateArgs, validate=False
                    )
                )
            except Exception as e:
                raise e

        return out, err, status



    def __reboot(self) -> tuple:
        try:
            ssh = SSHSupplicant(self.connection, tcpTimeout=self.timeout)
            ssh.command(
                SSHCommandRun.__commandCompile(
                    self.command, self.userArgs, self.templateArgs),
                alwaysSuccess=True # reboot on RH does not return 0.
            )

            return self.__waitPowerOn()
        except Exception as e:
            raise e



    def __waitPowerOn(self) -> tuple:
        o = ""

        try:
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
                raise CustomException(status=400, payload={"SSH": "machine not responding."})

            return "", "", 0
        except Exception as e:
            raise e



    @staticmethod
    def __validateUserArgs(userArgs: dict, templateArgs: dict):
        # Validate user args against args template.

        try:
            # User args must be of the expected type (i.e. the type specified in the template args).
            for ku, vu in userArgs.items():
                if isinstance(vu, eval(templateArgs[ku])):
                    del(templateArgs[ku]) # delete to keep track of available args.
                else:
                    raise CustomException(status=400, payload={"SSH": "forbidden data type in args."})

            # All template args passed?
            if templateArgs:
                raise CustomException(status=400, payload={"SSH": "some args missing."})
        except KeyError:
            # Something not needed passed (causing a KeyError).
            raise CustomException(status=400, payload={"SSH": "some args not required."})



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

            # Replace ${__argument} in command with userArgs["__argument"] value.
            for k, v in userArgs.items():
                command = command.replace("${"+k+"}", str(v))

            return command
        except Exception as e:
            raise e
