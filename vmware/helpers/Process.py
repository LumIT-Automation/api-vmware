import os
import subprocess
from vmware.helpers.Log import Log


class Process:
    @staticmethod
    # Execute process and get its exit code and output.
    # Wrapping C/Bash exit status convention to Python True/False for "success".
    # Use shell command to get the public key from the private one.
    # Using paramiko instead works only if all the keys are of the same type,
    # because paramiko.from_private_key is a class method, which hardly works well in a for loop.
    def execSSHKeygen(privateKey: str):
        command = 'ssh-keygen -yf /dev/stdin <<< $(echo -n "$PRIV_KEY")'
        execution = {
            "success": False,
            "status": -100,
            "stdout": "",
            "stderr": ""
        }

        subEnv = os.environ.copy()
        subEnv["PRIV_KEY"] = privateKey

        subProc = subprocess.Popen(
            command,
            executable="/bin/bash",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=subEnv
        )

        try:
            Log.actionLog("Try paramiko local bash command: "+str(command))

            execution["stdout"], execution["stderr"] = subProc.communicate(timeout=15)
            execution["status"] = int(subProc.returncode)
        except subprocess.TimeoutExpired:
            subProc.kill()
            subProc.communicate()
        except Exception as e:
            raise e

        if execution["status"] == 0:
            execution["success"] = True

        Log.actionLog("Command result status: "+str(execution["status"]))

        return execution
