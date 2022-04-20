import subprocess
from vmware.helpers.Log import Log


class Process:
    @staticmethod
    # Execute process and get its exit code and output.
    # Wrapping C/Bash exit status convention to Python True/False for "success".
    def execCommandString(invocation: str, procEnv: dict):
        execution = {
            "success": False,
            "status": -100,
            "stdout": "",
            "stderr": ""
        }

        subProc = subprocess.Popen(
            invocation,
            executable="/bin/bash",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=procEnv
        )

        try:
            Log.actionLog("Try paramiko local bash command: "+str(invocation))

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
