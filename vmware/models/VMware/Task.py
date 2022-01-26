from vmware.helpers.vmware.VmwareHandler import VmwareHandler

from vmware.helpers.Log import Log



class Task(VmwareHandler):



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            self.getVMwareObject()
            info = {
                "entityName": self.vmwareObj.info.entityName,
                "entity_moId": self.vmwareObj.info.entity._GetMoId(),
                "queueTime": str(self.vmwareObj.info.queueTime),
                "startTime": str(self.vmwareObj.info.startTime),
                "progress": self.vmwareObj.info.progress,
                "state": self.vmwareObj.info.state
            }
            return info

        except Exception as e:
            raise e



    def cancel(self) -> None:
        try:
            self.getVMwareObject()
            self.vmwareObj.CancelTask()

        except Exception as e:
            raise e



    def setDescription(self, description: str = "") -> None:
        try:
            self.getVMwareObject()
            self.vmwareObj.SetTaskDescription(description)

        except Exception as e:
            raise e



    def getVMwareObject(self, refresh: bool = False, silent: bool = True) -> None:
        try:
            vClient = VmwareHandler.connectToAssetAndGetContentStatic(self.assetId, silent)
            taskManager = vClient.oCluster.taskManager
            for task in taskManager.recentTask:
                Log.log(task, 'TTTTTTTTTTTTTT')
                if task.info.key == self.moId:
                    self.vmwareObj = task

        except Exception as e:
            raise e
