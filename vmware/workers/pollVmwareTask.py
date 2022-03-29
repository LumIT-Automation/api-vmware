import time

from vmware.models.VMware.Task import Task
from vmware.models.Stage2.Target import Target

from vmware.helpers.Log import Log


def pollVmwareTask(assetId: int, taskMoId: str, targetId: int) -> None:
    timeout = 600 # [seconds]

    try:
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            Log.log("Celery worker for VMware task: "+taskMoId)

            # Get VMware task info.
            tsk = Task(assetId=assetId, moId=taskMoId)
            info = tsk.info()
            del tsk

            # Update db.
            Target(targetId=targetId).modify({
                "task_state": info["state"],
                "task_progress": info["progress"],
                "task_startTime": info["startTime"],
                "task_queueTime": info["queueTime"]
            })

            # Until success or error.
            if info["state"] == "success" \
                    or info["state"] == 'error':
                break

            time.sleep(10) # every 10s.

    except Exception as e:
        raise e
