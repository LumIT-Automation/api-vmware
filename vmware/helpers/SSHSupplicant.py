import paramiko
import io

from vmware.helpers.Log import Log
from vmware.helpers.Exception import CustomException


class SSHSupplicant:
    def __init__(self, dataConnection: dict, tcpTimeout: int = 10, silent: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in ["ip", "username"]:
            if key not in dataConnection:
                raise ValueError('Missing key in dataConnection dictionary.')

        self.ipAddr = dataConnection["ip"]
        if "port" in dataConnection and dataConnection["port"]:
            self.port = dataConnection["port"]
        else:
            self.port = 22
        self.username = dataConnection["username"]

        if "priv_key" in dataConnection and dataConnection["priv_key"]:
            keyStringIO = io.StringIO(dataConnection["priv_key"])
            self.privateKey = paramiko.RSAKey.from_private_key(keyStringIO)
        else:
            self.privateKey = None

        if "password" in dataConnection and dataConnection["password"]:
            self.password = dataConnection["password"]
        else:
            self.password = ""

        self.tcpTimeout = tcpTimeout
        self.silent = silent



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def command(self, cmd, alwaysSuccess: bool = False) -> tuple:
        # Execute an ssh command to the remote system defined in the dataConnection parameter.

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), paramiko will raise the applicable exception.
        # If an ssh command times out, a socket.timeout exception is raised.
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # auto add the remote ssh host key.

        try:
            if not self.silent:
                Log.actionLog("Try paramiko ssh command: "+str(cmd))

            if self.privateKey:
                Log.actionLog("Paramiko ssh connection: host: "+str(self.ipAddr)+" port: "+str(self.port)+" username: "+self.username+" ssh key auth.")
                ssh.connect(hostname=self.ipAddr, port=self.port, username=self.username, pkey=self.privateKey, timeout=self.tcpTimeout)
            elif self.username and self.password:
                Log.actionLog("Paramiko ssh connection: host: "+str(self.ipAddr)+" port: "+str(self.port)+" username: "+self.username)
                ssh.connect(hostname=self.ipAddr, port=self.port, username=self.username, password=self.password, timeout=self.tcpTimeout)
            else:
                raise CustomException(status=503, payload={"SSH": "failed to execute the SSH command."})

            stdIn, stdOut, stdErr = ssh.exec_command(cmd) # pre-cleaned command.

            # Exit status.
            exitStatus = stdOut.channel.recv_exit_status()
            Log.actionLog("Paramiko exit status: "+str(exitStatus))
            if alwaysSuccess and exitStatus != 0:
                exitStatus = 0

            # Stdout data.
            outlines = stdOut.readlines()
            stdOutData = ''.join(outlines)
            if not self.silent:
                Log.actionLog("Paramiko stdout: "+stdOutData)
            else:
                Log.actionLog("Paramiko stdout: silenced by caller.")

            # Stderr data.
            errLines = stdErr.readlines()
            stdErrData = ''.join(errLines)
            if stdErrData:
                Log.actionLog("Paramiko stderr: "+stdErrData)

            return stdOutData, stdErrData, exitStatus
        except Exception as e:
            raise e
        finally:
            ssh.close()
