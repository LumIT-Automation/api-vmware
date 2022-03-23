import time

from vmware.models.VMware.Task import Task
from vmware.models.Stage2.Target import Target

from vmware.helpers.Log import Log


def poolVmwareTask(assetId: int, taskMoId: str, targetId: int) -> None:
    # Gets vmware task information.
    timeout = 300  # [seconds]
    status = "undefined"

    try:
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            tsk = Task(assetId=assetId, moId=taskMoId)
            info = tsk.info()
            Log.log('Celery worker: VMware Task moId: '+taskMoId, '_')
            del tsk
            if info["state"] != status:
                tgt = Target(targetId=targetId)
                data = {
                    "task_status": info["state"]
                }
                tgt.modify(data)
                status = info["state"]

                if info["state"] == "success" or info["state"] == 'error':
                    break
            time.sleep(10)

    except Exception as e:
        raise e


