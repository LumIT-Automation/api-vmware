import subprocess
from vmware.helpers.Log import Log


class Process:
    @staticmethod
    def runProc(invocation: str) -> dict:
        # Executes process and get its exit code and output.
        # Wraps C/Bash exit status convention to Python True/False for "success".

        execution = {
            "success": False,
            "status": 1,
            "output": ""
        }

        try:
            #p = subprocess.run(invocation, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) # https://bandit.readthedocs.io/en/latest/plugins/b602_subprocess_popen_with_shell_equals_true.html
            p = subprocess.run(invocation.split(" "), check=True, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            execution["output"] = p.stdout # std. output.
            execution["status"] = int(p.returncode) # exit code.

            if execution["status"] == 0:
                execution["success"] = True
        except Exception as e:
            raise e

        return execution



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

        try:
            subProc = subprocess.Popen(invocation, executable='/bin/bash', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=procEnv)
            execution["stdout"], execution["stderr"] = subProc.communicate(timeout=15)
            execution["status"] = int(subProc.returncode)

        except TimeoutExpired:
            subProc.kill()
            execution["stdout"], execution["stderr"] = subProc.communicate(timeout=15)
            execution["status"] = int(subProc.returncode)

        except Exception as e:
            raise e

        # Process exit code.
        if execution["status"] == 0:
            execution["success"] = True

        return execution
