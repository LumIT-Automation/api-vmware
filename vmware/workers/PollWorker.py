import time

from vmware.models.VMware.Task import Task
from vmware.models.Stage2.Target import Target

from vmware.helpers.Log import Log


class PollWorker:
    def __init__(self, assetId: int, taskMoId: str, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.taskMoId = taskMoId
        self.targetId = targetId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self) -> None:
        timeout = 600 # [seconds]

        try:
            timeout_start = time.time()
            while time.time() < timeout_start + timeout:
                Log.log("Celery worker for VMware task: "+self.taskMoId)

                # Get VMware task info.
                tsk = Task(assetId=self.assetId, moId=self.taskMoId)
                info = tsk.info()
                del tsk

                # Update db.
                Target(targetId=self.targetId).modify({
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
