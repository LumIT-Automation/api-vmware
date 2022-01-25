from pyVmomi import vim, vmodl

from vmware.models.VmwareContractor import VmwareContractor

from vmware.helpers.VmwareHelper import VmwareHelper
from vmware.helpers.Log import Log



class Task(VmwareContractor):



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
            vClient = VmwareContractor.connectToAssetAndGetContentStatic(self.assetId, silent)
            taskManager = vClient.content.taskManager
            for task in taskManager.recentTask:
                Log.log(task, 'TTTTTTTTTTTTTT')
                if task.info.key == self.moId:
                    self.vmwareObj = task

        except Exception as e:
            raise e
