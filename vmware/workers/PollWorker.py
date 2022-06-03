from typing import List
import time

from vmware.models.VMware.Task import Task
from vmware.models.VMware.CustomSpec import CustomSpec
from vmware.models.Stage2.Target import Target
from vmware.models.Stage2.TargetCommandExecution import TargetCommandExecution

from vmware.helpers.SSHCommandRun import SSHCommandRun
from vmware.helpers.Log import Log


class PollWorker:
    def __init__(self, assetId: int, taskMoId: str, targetId: int, guestSpec: str, forceDisableSecondStage: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId: int = int(assetId)
        self.taskMoId: str = taskMoId
        self.targetId: int = int(targetId)
        self.guestSpec: str = guestSpec
        self.forceDisableSecondStage: bool = forceDisableSecondStage

        self.commands: List[dict] = Target(self.targetId, loadCommands=True).commands



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self) -> None:
        deployStatus = False
        globalExitStatus = 0
        Log.log("Celery worker for VMware task: "+self.taskMoId)

        try:
            # Wait for VMware VM cloning completion.
            deployStatus = self.checkDeployStatus()
            if deployStatus and not self.forceDisableSecondStage:
                # On successful vm creation.
                if self.commands:
                    # Update db/target.
                    Target(targetId=self.targetId).modify({"second_stage_state": "running"})

                    # Execute scheduled SSH commands.
                    time.sleep(50) # wait for guest spec apply (a reboot occurs).

                    for command in self.commands:
                        Log.actionLog("Executing command uuid "+command["uid"]+" with user params: "+str(command["user_args"]))

                        o, e, s = SSHCommandRun(
                            commandUid=command["uid"],
                            targetId=self.targetId,
                            userArgs=command["user_args"]
                        )()

                        # Save results into db/target_command_exec.
                        TargetCommandExecution.add({
                            "id_target_command": command["id_target_command"],
                            "stdout": o,
                            "stderr": e,
                            "exit_status": s # exit ok = 0.
                        })

                        globalExitStatus += s
                        time.sleep(2)

                # Delete guestSpec (never fail).
                if self.guestSpec:
                    try:
                        Log.actionLog("Deleting guest spec: "+str(self.guestSpec))
                        CustomSpec(self.assetId, self.guestSpec).delete()
                    except Exception:
                        pass
        except Exception:
            globalExitStatus = 1
        finally:
            if deployStatus and not self.forceDisableSecondStage:
                if self.commands:
                    # Update db/target.
                    v = "completed with errors"
                    if not globalExitStatus:
                        v = "completed with success"

                    Target(targetId=self.targetId).modify({
                        "second_stage_state": v
                    })



    def checkDeployStatus(self) -> bool:
        timeout = 1200 # [seconds]
        ret = False

        try:
            timeout_start = time.time()

            while True:
                # Get VMware task info.
                tsk = Task(assetId=self.assetId, moId=self.taskMoId)
                info = tsk.info()
                del tsk

                # Update db/target during normal operation.
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

                # Timeout reached.
                if time.time() >= timeout_start + timeout:
                    # Update db/target on timeout.
                    Target(targetId=self.targetId).modify({
                        "task_state": "error",
                        "task_progress": None,
                        "task_message": "Concerto Orchestration: Timeout reached during operation."
                    })
                    break

            return ret
        except Exception as e:
            # Update db/target on exception.
            Target(targetId=self.targetId).modify({
                "task_state": "error",
                "task_progress": None,
                "task_message": "Concerto Orchestration exception: VMware task not found."
            })

            raise e
