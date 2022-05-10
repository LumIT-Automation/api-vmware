from pyVmomi import vmodl

from vmware.helpers.Exception import CustomException
from vmware.helpers.VMware.VmwareHandler import VmwareHandler


class Task(VmwareHandler):
    def __init__(self, assetId: int, moId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.moId = moId
        self.oTask = self.__oTaskLoad()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def oCancel(self) -> None:
        try:
            self.oTask.CancelTask()
        except Exception as e:
            raise e



    def oSetDescription(self, description: str = "") -> None:
        try:
            oldDesc = self.oTask.info.description
            newDesc = vmodl.LocalizableMessage(key=oldDesc.key+'-concerto', message=description + oldDesc.message)
            self.oTask.SetTaskDescription(newDesc)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def oTasks(assetId) -> list:
        try:
            vmware = VmwareHandler()
            return vmware.getTaskManager(assetId=assetId).recentTask
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __oTaskLoad(self):
        try:
            taskManager = self.getTaskManager(assetId=self.assetId)
            for task in taskManager.recentTask:
                if task.info.key == self.moId:
                    return task
            raise CustomException(status=404, payload={"VMware": "cannot load resource."})
        except Exception as e:
            raise e
