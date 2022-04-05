import time

from vmware.models.VMware.Task import Task
from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.TargetCommand import TargetCommand

from vmware.helpers.Log import Log


class PollWorker:
    def __init__(self, assetId: int, taskMoId: str, targetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.taskMoId = taskMoId
        self.targetId = targetId
        self.command = TargetCommand.list(self.targetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self) -> None:
        Log.log("Celery worker for VMware task: " + self.taskMoId)

        try:
            if self.checkDeployStatus():
                for command in self.command:
                    Log.log(command, '_')
        except Exception as e:
            raise e



    def checkDeployStatus(self) -> bool:
        timeout = 600 # [seconds]
        ret = False

        try:
            timeout_start = time.time()
            while time.time() < timeout_start + timeout:
                # Get VMware task info.
                tsk = Task(assetId=self.assetId, moId=self.taskMoId)
                info = tsk.info()
                del tsk

                # Update db.
                Target(targetId=self.targetId).modify({
                    "task_state": info["state"],
                    "task_progress": info["progress"],
                    "task_startTime": info["startTime"],
                    "task_queueTime": info["queueTime"],
                    "task_message": info["message"]
                })

                # Until success or error.
                if info["state"] == "success":
                    ret = True
                    break
                elif info["state"] == "error":
                    break
                else:
                    time.sleep(10) # every 10s.

            return ret
        except Exception as e:
            raise e




