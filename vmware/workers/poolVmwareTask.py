import time

from vmware.models.VMware.Task import Task
from vmware.models.Stage2.Target import Target


def poolVmwareTask(assetId: int, taskMoId: str, targetId: int) -> None:
    # Gets vmware task information.

    timeout = 300  # [seconds]
    status = "undefined"
    tsk = Task(assetId=assetId, moId=taskMoId)
    info = tsk.info()
    try:
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            if info["state"] != status:
                tgt = Target(targetId=targetId)
                data = {
                    "task_status": info["state"]
                }
                tgt.modify(data)
                status = info["state"]

                if info["state"] == "successfully" or info["state"] == 'failed':
                    break

    except Exception as e:
        raise e


